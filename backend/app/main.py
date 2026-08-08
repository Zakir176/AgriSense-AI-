from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base, SessionLocal
from .models.farm import Farm
from .models.auth import User
from .routers.auth import get_password_hash
from .models.user_farm import UserFarmAssociation

# Import all models to register on Base
from .models import Base
from .routers import auth, farms, batches, readings, growth, medications, alerts, inference, spatial_trends, audio, scheduled_treatments, inventory

# Auto-create tables (practical for Phase 1 mockup)
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        # Seed default farm
        if db.query(Farm).count() == 0:
            default_farm = Farm(name="Prime Nest Poultry", location="Lusaka, Zambia")
            db.add(default_farm)
            db.commit()
            print("Successfully seeded database with default farm 'Prime Nest Poultry'")
            
        # Seed default user
        if db.query(User).filter(User.username == "operator").count() == 0:
            default_user = User(
                username="operator",
                hashed_password=get_password_hash("prime_nest_2026"),
                full_name="Evans Kabwe",
                is_admin=True
            )
            db.add(default_user)
            db.commit()
            print("Successfully seeded database with default user 'operator'")
        else:
            # Ensure existing operator has admin privileges (migration guard)
            existing_op = db.query(User).filter(User.username == "operator").first()
            if existing_op and not existing_op.is_admin:
                existing_op.is_admin = True
                db.commit()
                print("Promoted existing 'operator' user to admin")

        # Seed default user-farm relationship
        user = db.query(User).filter(User.username == "operator").first()
        farm = db.query(Farm).filter(Farm.name == "Prime Nest Poultry").first()
        if user and farm:
            assoc = db.query(UserFarmAssociation).filter(
                UserFarmAssociation.user_id == user.id,
                UserFarmAssociation.farm_id == farm.id
            ).first()
            if not assoc:
                assoc = UserFarmAssociation(user_id=user.id, farm_id=farm.id, role="owner")
                db.add(assoc)
                db.commit()
                print("Successfully seeded user-farm association (operator -> Prime Nest Poultry as owner)")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (move seed_database contents here)
    seed_database()
    yield
    # Shutdown logic (nothing needed for Phase 1)

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
    {"name": "Audio", "description": "Audio telemetry for heuristic distress call classification."}
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AgriSense AI API Service — Intelligent Poultry Farm Management.\n\nProvides endpoints for offline-first synchronization, YOLOv8 visual audits, audio telemetry, and daily farm metric logging.",
    version=settings.VERSION,
    openapi_tags=tags_metadata,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS — NOTE: allow_credentials=True requires explicit origins; "*" is NOT
# allowed by browsers when credentials are included in the request.
origins = [
    "http://localhost:5173",    # Vue dev server (Vite)
    "http://localhost:3000",    # Alternative local dev
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Add production Vercel URL from env if set
frontend_url = settings.FRONTEND_URL.strip()
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under V1 prefix
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(farms.router, prefix=settings.API_V1_STR)
app.include_router(batches.router, prefix=settings.API_V1_STR)
app.include_router(readings.router, prefix=settings.API_V1_STR)
app.include_router(growth.router, prefix=settings.API_V1_STR)
app.include_router(medications.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(inference.router, prefix=settings.API_V1_STR)
app.include_router(spatial_trends.router, prefix=settings.API_V1_STR)
app.include_router(audio.router, prefix=settings.API_V1_STR)
app.include_router(scheduled_treatments.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)

from fastapi.staticfiles import StaticFiles
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Live RTSP Simulator WebSocket ──────────────────
from fastapi import WebSocket, WebSocketDisconnect
import json as _json

@app.websocket("/ws/rtsp-stream/{batch_id}")
async def rtsp_stream(websocket: WebSocket, batch_id: int):
    """
    WebSocket endpoint that streams simulated RTSP video frames
    with YOLO bounding-box overlays and real-time telemetry JSON.
    """
    await websocket.accept()
    
    # Resolve expected bird count from the batch
    db = SessionLocal()
    try:
        from .models.batch import Batch
        from .models.reading import FeedWaterReading
        from sqlalchemy import func
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            await websocket.send_json({"error": "Batch not found"})
            await websocket.close()
            return
        cumulative_mortality = db.query(func.sum(FeedWaterReading.mortality_count)).filter(FeedWaterReading.batch_id == batch_id).scalar() or 0
        expected_count = max(0, batch.bird_count - cumulative_mortality)
    finally:
        db.close()

    try:
        from .services.rtsp_simulator import RTSPSimulator
        simulator = RTSPSimulator(expected_count=min(expected_count, 80))  # cap for performance
    except (ImportError, ModuleNotFoundError):
        await websocket.send_json({"error": "OpenCV / NumPy dependencies not installed for RTSP simulation."})
        await websocket.close()
        return

    try:
        async for payload in simulator.stream_frames():
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AgriSense AI API Service",
        "docs_url": "/docs",
        "version": settings.VERSION
    }

