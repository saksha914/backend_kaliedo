from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from ..core.database import get_database
from ..models.assessment import AssessmentResult, AssessmentResultResponse, AssessmentResponse
from ..utils.assessment import (
    get_shuffled_questions, 
    calculate_domain_scores, 
    calculate_descriptive_scores,
    calculate_total_score, 
    get_overall_rating, 
    get_domain_ratings,
    validate_responses
)
from ..services.user_service import UserService
from fastapi import HTTPException, status

class AssessmentService:
    def __init__(self):
        self.db = get_database()
        self.results_collection = self.db.assessment_results
        self.user_service = UserService(self.db.users)

    async def get_questions(self) -> List[Dict]:
        """Get shuffled assessment questions."""
        return get_shuffled_questions()

    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """Get question by ID from the shuffled questions."""
        questions = get_shuffled_questions()
        for q in questions:
            if q["id"] == question_id:
                return q
        return None

    async def submit_assessment_with_user_data(self, user_data: Dict, responses: List[AssessmentResponse], 
                                              started_at: datetime, completed_at: datetime) -> AssessmentResultResponse:
        """Submit assessment responses with user data and calculate results."""
        # Validate responses
        if not validate_responses(responses):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assessment responses"
            )
        
        # Calculate scores
        domain_scores = calculate_domain_scores(responses)
        descriptive_scores = calculate_descriptive_scores(responses)
        total_score = calculate_total_score(domain_scores)
        overall_rating = get_overall_rating(domain_scores)
        domain_ratings = get_domain_ratings(domain_scores)
        
        # Calculate time taken
        time_diff = completed_at - started_at
        total_time_minutes = int(time_diff.total_seconds() / 60)
        
        # Create assessment result
        result_data = {
            "user_data": user_data,
            "responses": [response.dict() for response in responses],
            "domain_scores": domain_scores,
            "descriptive_scores": descriptive_scores,
            "total_score": total_score,
            "overall_rating": overall_rating,
            "started_at": started_at,
            "completed_at": completed_at,
            "total_time_minutes": total_time_minutes,
            "created_at": datetime.utcnow()
        }
        
        # Save to database
        result = await self.results_collection.insert_one(result_data)
        result_data["_id"] = result.inserted_id
        
        # Create response
        return AssessmentResultResponse(
            id=str(result.inserted_id),
            user_data=user_data,
            domain_scores=domain_scores,
            descriptive_scores=descriptive_scores,
            total_score=total_score,
            overall_rating=overall_rating,
            domain_ratings=domain_ratings,
            started_at=started_at,
            completed_at=completed_at,
            total_time_minutes=total_time_minutes,
            created_at=result_data["created_at"]
        )

    async def get_assessment_result(self, assessment_id: str) -> Optional[AssessmentResultResponse]:
        """Get assessment result by ID."""
        try:
            result = await self.results_collection.find_one({"_id": ObjectId(assessment_id)})
            if not result:
                return None
            
            return AssessmentResultResponse(
                id=str(result["_id"]),
                user_data=result["user_data"],
                domain_scores=result["domain_scores"],
                descriptive_scores=result.get("descriptive_scores", {}),
                total_score=result["total_score"],
                overall_rating=result["overall_rating"],
                domain_ratings=result.get("domain_ratings", {}),
                started_at=result["started_at"],
                completed_at=result["completed_at"],
                total_time_minutes=result["total_time_minutes"],
                created_at=result["created_at"]
            )
        except:
            return None

    async def get_all_assessment_results(self) -> List[AssessmentResultResponse]:
        """Get all assessment results (admin only)."""
        cursor = self.results_collection.find().sort("created_at", -1)
        results = await cursor.to_list(length=None)
        
        return [
            AssessmentResultResponse(
                id=str(result["_id"]),
                user_data=result["user_data"],
                domain_scores=result["domain_scores"],
                descriptive_scores=result.get("descriptive_scores", {}),
                total_score=result["total_score"],
                overall_rating=result["overall_rating"],
                domain_ratings=result.get("domain_ratings", {}),
                started_at=result["started_at"],
                completed_at=result["completed_at"],
                total_time_minutes=result["total_time_minutes"],
                created_at=result["created_at"]
            )
            for result in results
        ]

    async def get_assessment_results_by_email(self, email: str) -> List[AssessmentResultResponse]:
        """Get assessment results for a specific user by email."""
        cursor = self.results_collection.find({"user_data.email": email}).sort("created_at", -1)
        results = await cursor.to_list(length=None)
        
        return [
            AssessmentResultResponse(
                id=str(result["_id"]),
                user_data=result["user_data"],
                domain_scores=result["domain_scores"],
                descriptive_scores=result.get("descriptive_scores", {}),
                total_score=result["total_score"],
                overall_rating=result["overall_rating"],
                domain_ratings=result.get("domain_ratings", {}),
                started_at=result["started_at"],
                completed_at=result["completed_at"],
                total_time_minutes=result["total_time_minutes"],
                created_at=result["created_at"]
            )
            for result in results
        ]

    async def get_overall_statistics(self) -> Dict:
        """Get overall assessment statistics."""
        pipeline = [
            {"$group": {
                "_id": None,
                "total_assessments": {"$sum": 1},
                "avg_total_score": {"$avg": "$total_score"},
                "avg_time_minutes": {"$avg": "$total_time_minutes"}
            }}
        ]
        
        stats = await self.results_collection.aggregate(pipeline).to_list(length=1)
        
        if not stats:
            return {
                "total_assessments": 0,
                "avg_total_score": 0,
                "avg_time_minutes": 0
            }
        
        return stats[0]

    async def get_domain_analysis(self, domain: str) -> Dict:
        """Get analysis for a specific domain."""
        pipeline = [
            {"$unwind": "$responses"},
            {"$match": {"responses.domain": domain}},
            {"$group": {
                "_id": "$responses.response",
                "count": {"$sum": 1},
                "total_responses": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        cursor = self.results_collection.aggregate(pipeline)
        domain_stats = await cursor.to_list(length=None)
        
        # Calculate domain averages
        domain_averages = await self.results_collection.aggregate([
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": f"$domain_scores.{domain}"},
                "total_assessments": {"$sum": 1}
            }}
        ]).to_list(length=1)
        
        return {
            "domain": domain,
            "response_distribution": domain_stats,
            "average_score": domain_averages[0]["avg_score"] if domain_averages else 0,
            "total_assessments": domain_averages[0]["total_assessments"] if domain_averages else 0
        } 