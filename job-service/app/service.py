"""
Job Service — business logic layer.
"""
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db


def _serialize_job(job: dict) -> dict:
    if not job:
        return None
    job["id"] = str(job.pop("_id"))
    if isinstance(job.get("posted_at"), datetime):
        job["posted_at"] = job["posted_at"].isoformat()
    else:
        job["posted_at"] = str(job.get("posted_at", ""))
    return job


async def create_job(data: dict) -> dict:
    db = get_db()
    job_doc = {
        "title": data["title"],
        "company": data["company"],
        "description": data["description"],
        "required_skills": [s.lower().strip() for s in data.get("required_skills", [])],
        "location": data.get("location", "Remote"),
        "salary_range": data.get("salary_range", {"min": 0, "max": 0}),
        "experience_level": data.get("experience_level", "mid"),
        "job_type": data.get("job_type", "full-time"),
        "posted_at": data.get("posted_at", datetime.now(timezone.utc)),
    }
    result = await db.jobs.insert_one(job_doc)
    job_doc["_id"] = result.inserted_id
    return _serialize_job(job_doc)


async def get_job(job_id: str) -> dict:
    db = get_db()
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        return None
    return _serialize_job(job)


async def list_jobs(skip: int = 0, limit: int = 50, filters: dict = None) -> tuple:
    db = get_db()
    query = {}
    if filters:
        if filters.get("experience_level"):
            query["experience_level"] = filters["experience_level"]
        if filters.get("job_type"):
            query["job_type"] = filters["job_type"]
        if filters.get("location"):
            query["location"] = {"$regex": filters["location"], "$options": "i"}
        if filters.get("skills"):
            query["required_skills"] = {"$in": [s.lower() for s in filters["skills"]]}

    total = await db.jobs.count_documents(query)
    cursor = db.jobs.find(query).sort("posted_at", -1).skip(skip).limit(limit)
    jobs = []
    async for job in cursor:
        jobs.append(_serialize_job(job))
    return jobs, total


async def search_jobs(query_text: str, limit: int = 20) -> list:
    db = get_db()
    if not query_text:
        return []
    cursor = db.jobs.find(
        {"$text": {"$search": query_text}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(limit)
    jobs = []
    async for job in cursor:
        job.pop("score", None)
        jobs.append(_serialize_job(job))
    return jobs


async def get_all_jobs_raw() -> list:
    """Get all jobs as raw dicts for the recommendation engine."""
    db = get_db()
    cursor = db.jobs.find({})
    jobs = []
    async for job in cursor:
        jobs.append(_serialize_job(job))
    return jobs


async def seed_jobs(jobs_data: list) -> int:
    db = get_db()
    count = await db.jobs.count_documents({})
    if count > 0:
        return count
    for job in jobs_data:
        await create_job(job)
    return len(jobs_data)


async def delete_all_jobs() -> int:
    db = get_db()
    result = await db.jobs.delete_many({})
    return result.deleted_count
