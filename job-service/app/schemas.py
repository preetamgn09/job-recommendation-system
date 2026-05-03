"""
Pydantic schemas for Job Service.
"""
from typing import Optional
from pydantic import BaseModel, Field

class SalaryRange(BaseModel):
    min: int = Field(0, ge=0)
    max: int = Field(0, ge=0)

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: list[str] = []
    location: str = "Remote"
    salary_range: SalaryRange = SalaryRange()
    experience_level: str = "mid"
    job_type: str = "full-time"

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    description: str
    required_skills: list[str]
    location: str
    salary_range: dict
    experience_level: str
    job_type: str
    posted_at: str

class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
