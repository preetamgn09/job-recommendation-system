"""
Recommendation Service — business logic.
"""
import httpx
from app.config import settings
from app.engine import engine
from app.cache import get_cached_recommendations, cache_recommendations, invalidate_cache
from app.database import get_db
from bson import ObjectId


async def _fetch_user(user_id: str) -> dict | None:
    """Fetch user from User Service or directly from MongoDB."""
    db = get_db()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user.pop("_id"))
            return user
    except Exception:
        pass
    # Fallback: try via HTTP
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.USER_SERVICE_URL}/users/{user_id}")
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return None


async def _fetch_all_jobs() -> list:
    """Fetch all jobs from Job Service or directly from MongoDB."""
    db = get_db()
    try:
        cursor = db.jobs.find({})
        jobs = []
        async for job in cursor:
            job["id"] = str(job.pop("_id"))
            if hasattr(job.get("posted_at"), "isoformat"):
                job["posted_at"] = job["posted_at"].isoformat()
            else:
                job["posted_at"] = str(job.get("posted_at", ""))
            jobs.append(job)
        return jobs
    except Exception:
        pass
    # Fallback: try via HTTP
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{settings.JOB_SERVICE_URL}/jobs/all-raw")
            if resp.status_code == 200:
                return resp.json().get("jobs", [])
    except Exception:
        pass
    return []


async def get_recommendations(user_id: str, top_n: int = None, force_recalc: bool = False) -> dict:
    """Get job recommendations for a user."""
    if top_n is None:
        top_n = settings.RECO_TOP_N

    # Check cache first (unless force recalc)
    if not force_recalc:
        cached = await get_cached_recommendations(user_id)
        if cached:
            return {"user_id": user_id, "recommendations": cached, "source": "cache", "count": len(cached)}

    # Fetch data
    user = await _fetch_user(user_id)
    if not user:
        return {"error": "User not found", "user_id": user_id}

    jobs = await _fetch_all_jobs()
    if not jobs:
        return {"user_id": user_id, "recommendations": [], "source": "computed", "count": 0}

    # Run recommendation engine
    engine.content_weight = settings.RECO_CONTENT_WEIGHT
    engine.activity_weight = settings.RECO_ACTIVITY_WEIGHT
    recommendations = engine.recommend(user, jobs, top_n=top_n)

    # Cache results
    await cache_recommendations(user_id, recommendations)

    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "source": "computed",
        "count": len(recommendations),
    }


async def get_similar_jobs(job_id: str, top_n: int = 5) -> dict:
    """Find jobs similar to a given job."""
    jobs = await _fetch_all_jobs()
    target_job = None
    for j in jobs:
        if j.get("id") == job_id:
            target_job = j
            break

    if not target_job:
        return {"error": "Job not found", "job_id": job_id}

    similar = engine.find_similar_jobs(target_job, jobs, top_n=top_n)
    return {"job_id": job_id, "similar_jobs": similar, "count": len(similar)}


async def recalculate(user_id: str) -> dict:
    """Force recalculate recommendations (invalidate cache first)."""
    await invalidate_cache(user_id)
    return await get_recommendations(user_id, force_recalc=True)
