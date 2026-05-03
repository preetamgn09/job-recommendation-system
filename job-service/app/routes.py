"""
Job Service — API routes.
"""
from fastapi import APIRouter, HTTPException, Query
import httpx
import re
from app.schemas import JobCreate, JobResponse, JobListResponse
from app import service
from app.seed import get_seed_jobs

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    experience_level: str = None,
    job_type: str = None,
    location: str = None,
    skills: str = None,
):
    filters = {}
    if experience_level:
        filters["experience_level"] = experience_level
    if job_type:
        filters["job_type"] = job_type
    if location:
        filters["location"] = location
    if skills:
        filters["skills"] = [s.strip() for s in skills.split(",")]
    jobs, total = await service.list_jobs(skip=skip, limit=limit, filters=filters if filters else None)
    return {"jobs": jobs, "total": total}


@router.get("/search")
async def search_jobs(q: str = Query(..., min_length=2), limit: int = Query(20, ge=1, le=50)):
    jobs = await service.search_jobs(q, limit=limit)
    return {"jobs": jobs, "total": len(jobs), "query": q}


@router.get("/all-raw")
async def get_all_raw():
    """Internal endpoint — returns all jobs for recommendation engine."""
    jobs = await service.get_all_jobs_raw()
    return {"jobs": jobs}


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(data: JobCreate):
    job = await service.create_job(data.model_dump())
    return job


@router.post("/seed")
async def seed_jobs():
    """Seed the database with 50 sample job listings."""
    jobs_data = get_seed_jobs()
    count = await service.seed_jobs(jobs_data)
    return {"message": f"Seeded {count} jobs", "count": count}


@router.post("/fetch-live")
async def fetch_live_jobs(limit: int = Query(50, ge=1, le=100)):
    """Fetch real live jobs from Remotive API and store them in the database."""
    url = f"https://remotive.com/api/remote-jobs?category=software-dev&limit={limit}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("jobs", [])[:limit]
            
            normalized_jobs = []
            for j in jobs:
                # Strip HTML from description
                desc = j.get("description", "")
                clean_desc = re.sub(r'<[^>]+>', '', desc)
                
                # Normalize tags as skills
                skills = j.get("tags", [])
                if not skills:
                    skills = ["software development", "remote"]
                
                # Determine experience
                title = j.get("title", "").lower()
                exp = "mid"
                if "senior" in title or "lead" in title:
                    exp = "senior"
                elif "junior" in title or "entry" in title:
                    exp = "junior"
                    
                job_data = {
                    "title": j.get("title", "Software Engineer"),
                    "company": j.get("company_name", "Unknown Company"),
                    "description": clean_desc[:2000] + "..." if len(clean_desc) > 2000 else clean_desc,
                    "skills": [str(s).lower().strip() for s in skills[:15]],
                    "experience_level": exp,
                    "job_type": "full-time",
                    "location": j.get("candidate_required_location", "Remote")
                }
                normalized_jobs.append(job_data)
                
            count = await service.seed_jobs(normalized_jobs)
            return {"message": f"Fetched and saved {count} live jobs", "count": count}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch live jobs: {str(e)}")


@router.delete("/all")
async def delete_all():
    count = await service.delete_all_jobs()
    return {"message": f"Deleted {count} jobs", "count": count}
