from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from ..core.database import get_database
from ..models.user import UserModel, UserResponse
from ..schemas.auth import UserCreate, AdminUserCreate, UserLogin, Token, TokenData
from ..services.user_service import UserService
from ..utils.auth import create_access_token, create_refresh_token, verify_token
from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new regular user (no authentication required)."""
    db = get_database()
    user_service = UserService(db.users)
    
    try:
        user = await user_service.create_user(user_data)
        return UserResponse(
            id=str(user.id),
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            phone=user.phone,
            company=user.company,
            position=user.position,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            assessment_completed=user.assessment_completed,
            assessment_started_at=user.assessment_started_at,
            assessment_completed_at=user.assessment_completed_at,
            role=user.role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/admin/register", response_model=UserResponse)
async def register_admin(user_data: AdminUserCreate):
    """Register a new admin user (requires authentication)."""
    db = get_database()
    user_service = UserService(db.users)
    
    try:
        user = await user_service.create_admin_user(user_data)
        return UserResponse(
            id=str(user.id),
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            phone=user.phone,
            company=user.company,
            position=user.position,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            assessment_completed=user.assessment_completed,
            assessment_started_at=user.assessment_started_at,
            assessment_completed_at=user.assessment_completed_at,
            role=user.role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login admin user and return access token."""
    db = get_database()
    user_service = UserService(db.users)
    
    user = await user_service.authenticate_user(
        user_credentials.email,
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await user_service.update_last_login(str(user.id))
    
    # Create tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token_data: dict):
    """Refresh access token."""
    refresh_token = refresh_token_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    payload = verify_token(refresh_token, is_refresh=True)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    token_data = {"sub": payload.get("sub"), "username": payload.get("username"), "role": payload.get("role")}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Get current admin user information."""
    return UserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        company=current_user.company,
        position=current_user.position,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        assessment_completed=current_user.assessment_completed,
        assessment_started_at=current_user.assessment_started_at,
        assessment_completed_at=current_user.assessment_completed_at,
        role=current_user.role
    ) 
