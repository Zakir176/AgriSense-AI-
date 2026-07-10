"""
spatial_trends.py — Aggregated Spatial Health Trend Data
========================================================
Joins daily FeedWaterReading temperatures with InferenceResult clustering
metrics to produce a time-series suitable for dual-axis charting.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from ..database import get_db
from ..models.reading import FeedWaterReading
from ..models.media import MediaClip, InferenceResult
from ..models.batch import Batch
from ..models.auth import User
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/spatial-trends", tags=["Spatial Trends"])


class SpatialTrendPoint(BaseModel):
    date: date
    clustering_density_pct: Optional[float] = None
    spatial_dispersion_index: Optional[float] = None
    temperature_celsius: Optional[float] = None
    huddling_risk: str  # "low", "moderate", "high"


def classify_huddling_risk(density: Optional[float]) -> str:
    if density is None:
        return "low"
    if density > 65:
        return "high"
    if density >= 30:
        return "moderate"
    return "low"


@router.get("/{batch_id}", response_model=List[SpatialTrendPoint])
def get_spatial_trends(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    get_user_farm(batch.farm_id, current_user, db)

    # ── Gather daily temperature readings ─────────────────────────────────
    readings = (
        db.query(FeedWaterReading)
        .filter(FeedWaterReading.batch_id == batch_id)
        .order_by(FeedWaterReading.date.asc())
        .all()
    )

    temp_by_date = {}
    for r in readings:
        temp_by_date[r.date] = r.temperature_celsius

    # ── Gather inference results for this batch ───────────────────────────
    # Join MediaClip → InferenceResult, filter by batch_id
    inference_rows = (
        db.query(InferenceResult, MediaClip.uploaded_at)
        .join(MediaClip, InferenceResult.media_clip_id == MediaClip.id)
        .filter(MediaClip.batch_id == batch_id)
        .order_by(MediaClip.uploaded_at.asc())
        .all()
    )

    # Group inference results by date, averaging if multiple clips per day
    clustering_by_date = {}
    dispersion_by_date = {}
    for inf, uploaded_at in inference_rows:
        d = uploaded_at.date() if hasattr(uploaded_at, 'date') else uploaded_at
        if d not in clustering_by_date:
            clustering_by_date[d] = []
            dispersion_by_date[d] = []
        if inf.clustering_density_pct is not None:
            clustering_by_date[d].append(inf.clustering_density_pct)
        if inf.spatial_dispersion_index is not None:
            dispersion_by_date[d].append(inf.spatial_dispersion_index)

    # ── Build unified timeline ────────────────────────────────────────────
    all_dates = sorted(set(list(temp_by_date.keys()) + list(clustering_by_date.keys())))

    result = []
    for d in all_dates:
        cluster_vals = clustering_by_date.get(d, [])
        dispersion_vals = dispersion_by_date.get(d, [])

        avg_clustering = round(sum(cluster_vals) / len(cluster_vals), 1) if cluster_vals else None
        avg_dispersion = round(sum(dispersion_vals) / len(dispersion_vals), 1) if dispersion_vals else None
        temp = temp_by_date.get(d)

        result.append(SpatialTrendPoint(
            date=d,
            clustering_density_pct=avg_clustering,
            spatial_dispersion_index=avg_dispersion,
            temperature_celsius=temp,
            huddling_risk=classify_huddling_risk(avg_clustering),
        ))

    return result
