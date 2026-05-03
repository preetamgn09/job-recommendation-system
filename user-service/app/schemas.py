"""
Pydantic schemas for User Service request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# ── Request Schemas ──────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5)
    skills: list[str] = Field(default_factory=list)
    experience_years: int = Field(default=0, ge=0)
    preferred_roles: list[str] = Field(default_factory=list)
    location: str = Field(default="")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[list[str]] = None
    experience_years: Optional[int] = None
    preferred_roles: Optional[list[str]] = None
    location: Optional[str] = None


class ActivityLog(BaseModel):
    activity_type: str = Field(..., description="job_clicked, job_applied, job_searched")
    job_id: Optional[str] = None
    search_query: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


# ── Response Schemas ─────────────────────────────────────────

class ActivityResponse(BaseModel):
    activity_type: str
    job_id: Optional[str] = None
    search_query: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    timestamp: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    skills: list[str]
    experience_years: int
    preferred_roles: list[str]
    location: str
    activity: list[ActivityResponse] = Field(default_factory=list)
    created_at: str


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
