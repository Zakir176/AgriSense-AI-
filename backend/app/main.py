from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base

# Import all models to register on Base
from .models import Base
from .routers import auth, farms, batches, readings, growth, medications, alerts, inference

# Auto-create tables (practical for Phase 1 mockup)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS — NOTE: allow_credentials=True requires explicit origins; "*" is NOT
# allowed by browsers when credentials are included in the request.
origins = [
    "http://localhost:5173",    # Vue dev server (Vite)
    "http://localhost:3000",    # Alternative local dev
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

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

from fastapi.staticfiles import StaticFiles
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

from .database import SessionLocal
from .models.farm import Farm
from .models.auth import User
from .routers.auth import get_password_hash

@app.on_event("startup")
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
                full_name="Evans Kabwe"
            )
            db.add(default_user)
            db.commit()
            print("Successfully seeded database with default user 'operator' (password: prime_nest_2026)")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AgriSense AI API Service",
        "docs_url": "/docs",
        "version": settings.VERSION
    }
