from datetime import datetime
from typing import Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return handler(ObjectId)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

class UserModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "company": "Tech Corp",
                "position": "Manager",
                "is_active": True,
                "is_verified": False
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    full_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    # Authentication fields (only for admin users)
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    assessment_completed: bool = False
    assessment_started_at: Optional[datetime] = None
    assessment_completed_at: Optional[datetime] = None
    role: str = Field(default="user", description="Role of the user: user or admin")

class UserResponse(BaseModel):
    model_config = ConfigDict(json_encoders={ObjectId: str})
    
    id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    assessment_completed: bool
    assessment_started_at: Optional[datetime] = None
    assessment_completed_at: Optional[datetime] = None
    role: str = "user" 