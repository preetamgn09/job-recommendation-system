"""
User Service — business logic layer.
"""

from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db
from app.schemas import UserCreate, UserUpdate, ActivityLog


def _serialize_user(user: dict) -> dict:
    """Convert MongoDB document to API-friendly dict."""
    if not user:
        return None
    user["id"] = str(user.pop("_id"))
    user["created_at"] = user.get("created_at", "").isoformat() if isinstance(user.get("created_at"), datetime) else str(user.get("created_at", ""))
    # Serialize activity timestamps
    for act in user.get("activity", []):
        if isinstance(act.get("timestamp"), datetime):
            act["timestamp"] = act["timestamp"].isoformat()
    return user


async def create_user(data: UserCreate) -> dict:
    """Create a new user."""
    db = get_db()
    user_doc = {
        "name": data.name,
        "email": data.email,
        "skills": [s.lower().strip() for s in data.skills],
        "experience_years": data.experience_years,
        "preferred_roles": data.preferred_roles,
        "location": data.location,
        "activity": [],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return _serialize_user(user_doc)


async def get_user(user_id: str) -> dict:
    """Get a user by ID."""
    db = get_db()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    return _serialize_user(user)


async def update_user(user_id: str, data: UserUpdate) -> dict:
    """Update user profile."""
    db = get_db()
    update_fields = {}
    if data.name is not None:
        update_fields["name"] = data.name
    if data.skills is not None:
        update_fields["skills"] = [s.lower().strip() for s in data.skills]
    if data.experience_years is not None:
        update_fields["experience_years"] = data.experience_years
    if data.preferred_roles is not None:
        update_fields["preferred_roles"] = data.preferred_roles
    if data.location is not None:
        update_fields["location"] = data.location

    if not update_fields:
        return await get_user(user_id)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields}
    )
    return await get_user(user_id)


async def log_activity(user_id: str, data: ActivityLog) -> dict:
    """Log user activity (click, apply, search)."""
    db = get_db()
    activity_entry = {
        "activity_type": data.activity_type,
        "job_id": data.job_id,
        "search_query": data.search_query,
        "metadata": data.metadata,
        "timestamp": datetime.now(timezone.utc),
    }
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"activity": {"$each": [activity_entry], "$slice": -100}}}
    )
    return await get_user(user_id)


async def get_activity(user_id: str, limit: int = 20) -> list[dict]:
    """Get recent activity for a user."""
    db = get_db()
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)},
        {"activity": {"$slice": -limit}}
    )
    if not user:
        return []
    activities = user.get("activity", [])
    for act in activities:
        if isinstance(act.get("timestamp"), datetime):
            act["timestamp"] = act["timestamp"].isoformat()
    return list(reversed(activities))


async def get_all_users(skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
    """Get all users with pagination."""
    db = get_db()
    total = await db.users.count_documents({})
    cursor = db.users.find({}).skip(skip).limit(limit)
    users = []
    async for user in cursor:
        users.append(_serialize_user(user))
    return users, total


async def delete_user(user_id: str) -> bool:
    """Delete a user."""
    db = get_db()
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0
