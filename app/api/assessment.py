from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from ..models.assessment import AssessmentResponse, AssessmentResultResponse, AssessmentSubmission
from ..models.user import UserModel
from ..services.assessment_service import AssessmentService
from ..services.user_service import UserService
from ..api.deps import get_current_active_user
from ..core.database import get_database

router = APIRouter(prefix="/assessment", tags=["Assessment"])

@router.get("/questions")
async def get_assessment_questions():
    """Get shuffled assessment questions (no authentication required)."""
    assessment_service = AssessmentService()
    questions = await assessment_service.get_questions()
    
    # Remove domain information from questions for users
    user_questions = []
    for q in questions:
        user_question = {
            "id": q["id"],
            "question_text": q["question_text"],
            "question_number": q["question_number"],
            "type": q["type"]
        }
        user_questions.append(user_question)
    
    return {
        "questions": user_questions,
        "total_questions": len(user_questions),
        "domains": ["leadership", "accountability", "communication", "innovation", "sales", "ethics", "collaboration"]
    }

@router.post("/submit")
async def submit_assessment(submission: AssessmentSubmission):
    """Submit assessment responses (no authentication required)."""
    assessment_service = AssessmentService()
    
    # Convert string dates to datetime
    started_at = datetime.fromisoformat(submission.started_at.replace('Z', '+00:00'))
    completed_at = datetime.fromisoformat(submission.completed_at.replace('Z', '+00:00'))
    
    # Add domain information back to responses for processing
    processed_responses = []
    for response in submission.responses:
        # Find the original question to get domain info
        question = assessment_service.get_question_by_id(response.question_id)
        if question:
            processed_response = AssessmentResponse(
                question_id=response.question_id,
                response=response.response,
                domain=question["domain"],
                question_type=question["type"]
            )
            processed_responses.append(processed_response)
    
    try:
        result = await assessment_service.submit_assessment_with_user_data(
            submission.user_data,
            processed_responses,
            started_at,
            completed_at
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/results/{assessment_id}")
async def get_assessment_result(assessment_id: str):
    """Get assessment result by ID (no authentication required)."""
    assessment_service = AssessmentService()
    result = await assessment_service.get_assessment_result(assessment_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment result not found"
        )
    
    return result

# Admin-only endpoints (require authentication)
@router.get("/admin/results")
async def get_all_assessment_results(current_user: UserModel = Depends(get_current_active_user)):
    """Get all assessment results (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    assessment_service = AssessmentService()
    results = await assessment_service.get_all_assessment_results()
    return results

@router.get("/admin/results/{user_email}")
async def get_user_assessment_results(user_email: str, current_user: UserModel = Depends(get_current_active_user)):
    """Get assessment results for a specific user (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    assessment_service = AssessmentService()
    results = await assessment_service.get_assessment_results_by_email(user_email)
    return results 