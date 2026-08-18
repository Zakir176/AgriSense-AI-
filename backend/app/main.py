import logging
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse

from .config import settings
from .database import engine, Base, SessionLocal, get_db
from .limiter import limiter

# Import all models to register on Base metadata
from .models import Base  # noqa: F811
from .routers import (
    auth, farms, batches, readings, growth, medications, alerts,
    inference, spatial_trends, audio, scheduled_treatments, inventory, financial,
)

logger = logging.getLogger(__name__)

# ── Database bootstrap ──────────────────────────────────────────────────────
# Auto-create any missing tables on startup (safe / idempotent).
# Schema is managed via Alembic — run `alembic upgrade head` for migrations.
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: no automatic seeding.
    # Run `python seed_data.py` (with SEED_DEMO_PASSWORD set) to initialise
    # the database for the first time.
    yield
    # Shutdown: nothing needed.


# ── OpenAPI metadata ────────────────────────────────────────────────────────
tags_metadata = [
    {"name": "Auth", "description": "Authentication and JWT token management."},
    {"name": "Farms", "description": "Farm entity management and role-based access."},
    {"name": "Batches", "description": "Poultry batch lifecycle and archiving."},
    {"name": "Readings", "description": "Daily feed, water, and mortality logs."},
    {"name": "Growth", "description": "Weekly weight sampling and Cobb 500 reference tracking."},
    {"name": "Medications", "description": "Historical medical and vaccination logs."},
    {"name": "Scheduled Treatments", "description": "Interactive calendar for planning future treatments."},
    {"name": "Alerts", "description": "Heuristic anomaly alerts (mortality spikes, consumption drops)."},
    {"name": "Inference", "description": "YOLOv8 visual monitoring, flock counting, and activity scoring."},
    {"name": "Spatial Trends", "description": "Heatmaps and spatial distribution analysis."},
    {"name": "Audio", "description": "Audio telemetry for heuristic distress call classification."},
    {"name": "Inventory", "description": "Flock inventory adjustments: sales, mortality, culls, additions."},
    {"name": "Financial", "description": "Financial intelligence: expenses, revenue, P&L, and income forecasting."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AgriSense AI API Service — Intelligent Poultry Farm Management.\n\n"
        "Provides endpoints for offline-first synchronization, YOLOv8 visual audits, "
        "audio telemetry, and daily farm metric logging."
    ),
    version=settings.VERSION,
    openapi_tags=tags_metadata,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# ── Rate limiter (F-04) ─────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ────────────────────────────────────────────────────────────────────
# NOTE: allow_credentials=True requires explicit origins; "*" is NOT
# allowed by browsers when credentials are present in the request.
origins = [
    "http://localhost:5173",   # Vue dev server (Vite)
    "http://localhost:3000",   # Alternative local dev
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

frontend_url = settings.FRONTEND_URL.strip()
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Security response headers (F-12) ────────────────────────────────────────
# Applied to every response. HSTS is intentionally excluded — it should only
# be set at the TLS terminator (Railway / Nginx), not the app server.
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: StarletteRequest, call_next
    ) -> StarletteResponse:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ── API routers ─────────────────────────────────────────────────────────────
app.include_router(auth.router,                  prefix=settings.API_V1_STR)
app.include_router(farms.router,                 prefix=settings.API_V1_STR)
app.include_router(batches.router,               prefix=settings.API_V1_STR)
app.include_router(readings.router,              prefix=settings.API_V1_STR)
app.include_router(growth.router,                prefix=settings.API_V1_STR)
app.include_router(medications.router,           prefix=settings.API_V1_STR)
app.include_router(alerts.router,                prefix=settings.API_V1_STR)
app.include_router(inference.router,             prefix=settings.API_V1_STR)
app.include_router(spatial_trends.router,        prefix=settings.API_V1_STR)
app.include_router(audio.router,                 prefix=settings.API_V1_STR)
app.include_router(scheduled_treatments.router,  prefix=settings.API_V1_STR)
app.include_router(inventory.router,             prefix=settings.API_V1_STR)
app.include_router(financial.router,             prefix=settings.API_V1_STR)

# ── Uploads directory ───────────────────────────────────────────────────────
# The /uploads static mount has been intentionally removed (F-06).
# Files are served only via the authenticated route below.
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# ── Authenticated file-serving route (F-06) ─────────────────────────────────
from .routers.auth import get_current_user          # noqa: E402
from .models.auth import User                        # noqa: E402
from .models.media import MediaClip                  # noqa: E402
from .models.batch import Batch                      # noqa: E402
from .models.user_farm import UserFarmAssociation    # noqa: E402


@app.get(f"{settings.API_V1_STR}/uploads/{{filename}}")
def serve_upload(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Serve an uploaded video/audio file to authenticated, farm-authorised users.
    Replaces the previous unauthenticated static file mount at /uploads/.
    """
    # Prevent path traversal — filename must be a bare name with no separators.
    safe = os.path.basename(filename)
    if safe != filename or not safe:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    # Look up the MediaClip record so we can perform the farm ownership check.
    # UUID filenames make collisions astronomically unlikely.
    clip = (
        db.query(MediaClip)
        .filter(MediaClip.file_url.like(f"%{safe}"))
        .first()
    )
    if not clip:
        raise HTTPException(status_code=404, detail="File not found.")

    # Authorise: user must have a UserFarmAssociation for the clip's farm.
    batch = db.query(Batch).filter(Batch.id == clip.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="File not found.")

    assoc = (
        db.query(UserFarmAssociation)
        .filter(
            UserFarmAssociation.user_id == current_user.id,
            UserFarmAssociation.farm_id == batch.farm_id,
        )
        .first()
    )
    if not assoc:
        raise HTTPException(status_code=403, detail="You do not have access to this file.")

    file_path = os.path.join(settings.UPLOAD_DIR, safe)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(file_path)


# ── Live RTSP Simulator WebSocket (F-03 — authenticated) ────────────────────
from jose import JWTError, jwt as _jwt  # noqa: E402


@app.websocket("/ws/rtsp-stream/{batch_id}")
async def rtsp_stream(
    websocket: WebSocket,
    batch_id: int,
    token: str = Query(default=None),
):
    """
    WebSocket endpoint that streams simulated RTSP video frames with YOLO
    bounding-box overlays and real-time telemetry JSON.

    Authentication: pass the JWT as ?token=<access_token> in the URL.
    The connection is rejected (close code 4001) if no valid token is supplied,
    or if the authenticated user does not have access to the requested batch's farm.
    """
    # ── Step 1: validate the JWT before accepting the connection ──
    if not token:
        await websocket.close(code=4001)
        return

    try:
        payload = _jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    # ── Step 2: verify farm ownership before accepting ──
    db = SessionLocal()
    expected_count = 0
    try:
        from .models.auth import User as _User
        from .models.user_farm import UserFarmAssociation as _UFA
        from .models.batch import Batch as _Batch
        from .models.reading import FeedWaterReading
        from sqlalchemy import func

        user = db.query(_User).filter(_User.username == username).first()
        if not user:
            await websocket.close(code=4001)
            return

        batch = db.query(_Batch).filter(_Batch.id == batch_id).first()
        if not batch:
            await websocket.close(code=4004)
            return

        assoc = (
            db.query(_UFA)
            .filter(
                _UFA.user_id == user.id,
                _UFA.farm_id == batch.farm_id,
            )
            .first()
        )
        if not assoc:
            await websocket.close(code=4003)
            return

        cumulative_mortality = (
            db.query(func.sum(FeedWaterReading.mortality_count))
            .filter(FeedWaterReading.batch_id == batch_id)
            .scalar()
            or 0
        )
        expected_count = max(0, batch.bird_count - cumulative_mortality)
    finally:
        db.close()

    # ── Step 3: connection authorised — accept and stream ──
    await websocket.accept()

    try:
        from .services.rtsp_simulator import RTSPSimulator
        simulator = RTSPSimulator(expected_count=min(expected_count, 80))
    except (ImportError, ModuleNotFoundError):
        await websocket.send_json(
            {"error": "OpenCV / NumPy dependencies not installed for RTSP simulation."}
        )
        await websocket.close()
        return

    try:
        async for payload in simulator.stream_frames():
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


# ── Root health-check ────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "message": "Welcome to AgriSense AI API Service",
        "version": settings.VERSION,
    }
