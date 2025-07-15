from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from .user import PyObjectId
from ..models.user import UserResponse

class QuestionModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    question_text: str
    domain: str  # leadership, accountability, communication, innovation, sales, ethics, collaboration
    question_number: int
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = Field(default="mcq", description="mcq or descriptive")
    options: Optional[List[str]] = None  # Only for MCQ

class AssessmentResponse(BaseModel):
    question_id: str
    response: int  # 1-5 scale for MCQ, 0-3 for descriptive
    domain: str
    question_type: str = "mcq"  # mcq or descriptive

class AssessmentSubmission(BaseModel):
    user_data: Dict[str, Any]  # name, email, phone, company, position
    responses: List[AssessmentResponse]
    started_at: str
    completed_at: str

class AssessmentResult(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_data: Dict[str, Any]  # name, email, phone, company, position
    responses: List[AssessmentResponse]
    domain_scores: Dict[str, int]
    descriptive_scores: Dict[str, int]
    total_score: int
    overall_rating: str  # exemplary, strength, developing, weakness, critical
    started_at: datetime
    completed_at: datetime
    total_time_minutes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssessmentResultResponse(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    id: str
    user_data: Dict[str, Any]
    domain_scores: Dict[str, int]
    descriptive_scores: Dict[str, int]
    total_score: int
    overall_rating: str
    domain_ratings: Dict[str, str]
    started_at: datetime
    completed_at: datetime
    total_time_minutes: int
    created_at: datetime 