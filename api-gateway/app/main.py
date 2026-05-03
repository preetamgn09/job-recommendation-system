"""
API Gateway — FastAPI application entry point.

Routes all requests to downstream microservices:
  /api/users/*            → User Service :8001
  /api/jobs/*             → Job Service :8002
  /api/recommendations/*  → Recommendation Service :8003
  /api/events/publish     → Publish events to RabbitMQ
  /                       → Serve frontend dashboard
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.proxy import proxy_request
from app.middleware import RequestLoggingMiddleware
from app.events import publish_event
from pydantic import BaseModel
from typing import Optional


app = FastAPI(
    title="NextStep — API Gateway",
    description="Central entry point for the distributed job recommendation system",
    version="1.0.0",
)

# Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Event Publishing Endpoint ────────────────────────────────

class EventRequest(BaseModel):
    event_type: str
    user_id: str
    data: Optional[dict] = None


@app.post("/api/events/publish")
async def publish(event: EventRequest):
    """Publish an event to RabbitMQ via the gateway."""
    await publish_event(
        settings.RABBITMQ_URL,
        event.event_type,
        event.user_id,
        event.data,
    )
    return {"message": "Event published", "event_type": event.event_type}


# ── Health Check ─────────────────────────────────────────────

@app.get("/api/health")
async def gateway_health():
    return {"status": "healthy", "service": "api-gateway"}


# ── User Service Proxy ───────────────────────────────────────

@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_users(request: Request, path: str):
    target = f"{settings.USER_SERVICE_URL}/users/{path}"
    return await proxy_request(request, target)


# ── Job Service Proxy ────────────────────────────────────────

@app.api_route("/api/jobs/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_jobs(request: Request, path: str):
    target = f"{settings.JOB_SERVICE_URL}/jobs/{path}"
    return await proxy_request(request, target)

@app.api_route("/api/jobs", methods=["GET", "POST"])
async def proxy_jobs_root(request: Request):
    target = f"{settings.JOB_SERVICE_URL}/jobs/"
    return await proxy_request(request, target)


# ── Recommendation Service Proxy ─────────────────────────────

@app.api_route("/api/recommendations/{path:path}", methods=["GET", "POST"])
async def proxy_recommendations(request: Request, path: str):
    target = f"{settings.RECOMMENDATION_SERVICE_URL}/recommendations/{path}"
    return await proxy_request(request, target)


# ── Static Files (Frontend Dashboard) ────────────────────────

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_dashboard():
        return FileResponse(os.path.join(static_dir, "index.html"))
