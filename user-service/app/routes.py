"""
User Service — API routes.
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from app.schemas import UserCreate, UserUpdate, UserResponse, UserListResponse, ActivityLog
from app import service
from app.resume_parser import extract_text_from_pdf, extract_skills_from_text

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(data: UserCreate):
    """Register a new user with profile data."""
    try:
        user = await service.create_user(data)
        return user
    except Exception as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register/resume", response_model=UserResponse, status_code=201)
async def register_user_with_resume(
    name: str = Form(...),
    email: str = Form(...),
    location: str = Form(None),
    file: UploadFile = File(...)
):
    """Register a new user by parsing their resume PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        contents = await file.read()
        text = extract_text_from_pdf(contents)
        skills = extract_skills_from_text(text)
        
        # Simple rudimentary experience extraction
        experience = 0
        text_lower = text.lower()
        if "lead" in text_lower or "manager" in text_lower:
            experience = 8
        elif "senior" in text_lower or "architect" in text_lower:
            experience = 5
        elif "mid" in text_lower:
            experience = 3
        else:
            experience = 1
            
        data = UserCreate(
            name=name,
            email=email,
            location=location,
            skills=skills,
            experience_years=experience,
            preferred_roles=["Software Engineer", "Developer"] # Default generic roles
        )
        
        user = await service.create_user(data)
        return user
    except Exception as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already registered")
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@router.get("/", response_model=UserListResponse)
async def list_users(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    """List all users with pagination."""
    users, total = await service.get_all_users(skip=skip, limit=limit)
    return {"users": users, "total": total}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user profile by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, data: UserUpdate):
    """Update user profile."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = await service.update_user(user_id, data)
    return updated


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user."""
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted", "id": user_id}


@router.post("/{user_id}/activity", response_model=UserResponse)
async def log_activity(user_id: str, data: ActivityLog):
    """Log user activity (click, apply, search)."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated = await service.log_activity(user_id, data)
    return updated


@router.get("/{user_id}/activity")
async def get_activity(user_id: str, limit: int = Query(20, ge=1, le=100)):
    """Get recent activity for a user."""
    activities = await service.get_activity(user_id, limit=limit)
    return {"user_id": user_id, "activities": activities, "count": len(activities)}
