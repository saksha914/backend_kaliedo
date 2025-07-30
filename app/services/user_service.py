from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from passlib.context import CryptContext
from ..models.user import UserModel, UserResponse
from ..schemas.auth import UserCreate, AdminUserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, collection):
        self.collection = collection

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(self, user_data: UserCreate) -> UserModel:
        """Create a new regular user (no authentication required)."""
        # Check if email already exists
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user without authentication
        hashed_password = self.get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["role"] = "user"
        
        result = await self.collection.insert_one(user_dict)
        user_dict["id"] = result.inserted_id
        return UserModel(**user_dict)

    async def create_admin_user(self, user_data: AdminUserCreate) -> UserModel:
        """Create a new admin user with authentication."""
        # Check if username already exists
        existing_user = await self.collection.find_one({"username": user_data.username})
        if existing_user:
            raise ValueError("Username already taken")

        # Check if email already exists
        existing_email = await self.collection.find_one({"email": user_data.email})
        if existing_email:
            raise ValueError("Email already registered")

        # Create new admin user
        hashed_password = self.get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["role"] = "admin"
        
        result = await self.collection.insert_one(user_dict)
        user_dict["id"] = result.inserted_id
        return UserModel(**user_dict)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        """Authenticate user with email and password."""
        user = await self.collection.find_one({"email": email})
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        return UserModel(**user)

    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID."""
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            return UserModel(**user) if user else None
        except:
            return None

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get admin user by username."""
        user = await self.collection.find_one({"username": username, "role": "admin"})
        return UserModel(**user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email."""
        user = await self.collection.find_one({"email": email})
        return UserModel(**user) if user else None

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserModel]:
        """Update user information."""
        update_data = user_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return await self.get_user_by_id(user_id)
        return None

    async def update_last_login(self, user_id: str):
        """Update user's last login time."""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    async def mark_assessment_started(self, user_id: str):
        """Mark assessment as started for user."""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"assessment_started_at": datetime.utcnow()}}
        )

    async def mark_assessment_completed(self, user_id: str):
        """Mark assessment as completed for user."""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "assessment_completed": True,
                "assessment_completed_at": datetime.utcnow()
            }}
        )

    async def update_assessment_status(self, user_id: str, completed: bool = False):
        """Update user's assessment status."""
        update_data = {
            "assessment_completed": completed,
            "updated_at": datetime.utcnow()
        }
        
        if completed:
            update_data["assessment_completed_at"] = datetime.utcnow()
        else:
            update_data["assessment_started_at"] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

    async def get_all_users(self) -> List[UserResponse]:
        """Get all users (admin only)."""
        cursor = self.collection.find({})
        users = await cursor.to_list(length=None)
        return [UserResponse(**user) for user in users]

    async def get_users_by_role(self, role: str) -> List[UserResponse]:
        """Get users by role."""
        cursor = self.collection.find({"role": role})
        users = await cursor.to_list(length=None)
        return [UserResponse(**user) for user in users] 