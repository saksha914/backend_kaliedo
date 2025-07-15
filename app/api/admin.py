from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..models.assessment import QuestionModel, AssessmentResultResponse
from ..models.user import UserResponse
from ..core.database import get_database
from .deps import get_current_admin_user
from ..utils.assessment import get_domain_ratings  # Ensure this import is present

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/questions", response_model=QuestionModel)
async def add_question(question: QuestionModel, admin_user=Depends(get_current_admin_user)):
    db = get_database()
    result = await db.questions.insert_one(question.dict())
    question.id = result.inserted_id
    return question

@router.get("/questions", response_model=List[QuestionModel])
async def list_questions(admin_user=Depends(get_current_admin_user)):
    db = get_database()
    questions = await db.questions.find().to_list(length=1000)
    return questions

@router.get("/users", response_model=List[UserResponse])
async def list_users(admin_user=Depends(get_current_admin_user)):
    db = get_database()
    users = await db.users.find().to_list(length=1000)
    user_responses = []
    for u in users:
        user_responses.append(UserResponse(
            id=str(u.get("_id")),
            username=u.get("username", ""),
            full_name=u.get("full_name", ""),
            company=u.get("company", ""),
            position=u.get("position", ""),
            is_active=u.get("is_active", True),
            is_verified=u.get("is_verified", False),
            created_at=u.get("created_at"),
            assessment_completed=u.get("assessment_completed", False),
            assessment_started_at=u.get("assessment_started_at"),
            assessment_completed_at=u.get("assessment_completed_at"),
            role=u.get("role", "user")
        ))
    return user_responses

@router.get("/users/{user_id}/assessments", response_model=List[AssessmentResultResponse])
async def get_user_assessments(user_id: str, admin_user=Depends(get_current_admin_user)):
    db = get_database()
    results = await db.assessment_results.find({"user_id": user_id}).to_list(length=100)
    response_list = []
    for r in results:
        domain_ratings = r.get("domain_ratings")
        if not domain_ratings and "domain_scores" in r:
            domain_ratings = get_domain_ratings(r["domain_scores"])
        response_list.append(AssessmentResultResponse(
            id=str(r.get("_id")),
            user_id=r.get("user_id", ""),
            responses=r.get("responses", []),
            domain_scores=r.get("domain_scores", {}),
            total_score=r.get("total_score", 0),
            overall_rating=r.get("overall_rating", ""),
            domain_ratings=domain_ratings or {},
            started_at=r.get("started_at"),
            completed_at=r.get("completed_at"),
            total_time_minutes=r.get("total_time_minutes", 0),
            created_at=r.get("created_at")
        ))
    return response_list 