"""
Recommendation Service — API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from app import service
from app.cache import invalidate_all

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{user_id}")
async def get_recommendations(user_id: str, top_n: int = Query(10, ge=1, le=50)):
    """Get top-N job recommendations for a user."""
    result = await service.get_recommendations(user_id, top_n=top_n)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/{user_id}/recalculate")
async def recalculate(user_id: str):
    """Force recalculate recommendations (bypass cache)."""
    result = await service.recalculate(user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/similar-jobs/{job_id}")
async def similar_jobs(job_id: str, top_n: int = Query(5, ge=1, le=20)):
    """Find jobs similar to a given job."""
    result = await service.get_similar_jobs(job_id, top_n=top_n)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/cache/invalidate-all")
async def invalidate_cache():
    """Invalidate all cached recommendations."""
    await invalidate_all()
    return {"message": "All recommendation caches invalidated"}
