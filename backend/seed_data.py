"""
seed_data.py — AgriSense AI Demo Seed Script
=============================================
Data Source: Evans' REAL 200-bird broiler batch (6-week cycle)
Collected: June 2025

─────────────────────────────────────────────────────────────────────────────
Q1 — Weekly Feed & Water (200 birds)
─────────────────────────────────────────────────────────────────────────────
  Week 1:   35 kg feed  |   70 L water  (  5 kg/day |  10 L/day)
  Week 2:   53 kg feed  |  175 L water  (7.5 kg/day |  25 L/day)
  Week 3:  140 kg feed  |  245 L water  ( 20 kg/day |  35 L/day)
  Week 4:  210 kg feed  |  560 L water  ( 30 kg/day |  80 L/day)
  Week 5:  280 kg feed  |  700 L water  ( 40 kg/day | 100 L/day)
  Week 6:  350 kg feed  |  840 L water  ( 50 kg/day | 120 L/day)
  TOTALS: 1,068 kg feed (approx 22 x 50 kg bags) | 2,590 L water

─────────────────────────────────────────────────────────────────────────────
Q2 — Growth Samples (30 birds randomly picked each week)
─────────────────────────────────────────────────────────────────────────────
  Week 1: 40 - 50 g    -> midpoint  45 g
  Week 2: 160 - 200 g  -> midpoint 180 g
  Week 3: 800 g - 1 kg -> midpoint 900 g
  Week 4: 1.3 - 1.5 kg -> midpoint 1,400 g
  Week 5: 1.7 - 1.9 kg -> midpoint 1,800 g
  Week 6: 2.0 - 2.5 kg -> midpoint 2,250 g

─────────────────────────────────────────────────────────────────────────────
Q3 — Medication / Vaccination Schedule
─────────────────────────────────────────────────────────────────────────────
  Week 1  : Stress Pack              - 5 g (1 tsp) in 10 L water/day
  Week 2  : Chickens Formula         - 10 g (1 tbsp) in 20 L water/day
  Day 10  : Gumboro vaccine          - (200 x 10 x 1.5 / 1000) = 3.0 mL in 3 L water
  Day 14  : Newcastle vaccine        - (200 x 14 x 1.5 / 1000) = 4.2 mL in 4 L water
  Week 3  : Organic Mash booster     - 3 tbsp in 20 L water (daily)
  Day 18  : Gumboro booster          - (200 x 18 x 1.5 / 1000) = 5.4 mL in 5 L water
  Day 21  : Newcastle booster        - (200 x 21 x 1.5 / 1000) = 6.3 mL in 6 L water
  Week 4  : Organic Mash booster     - 3 tbsp in 20 L water (daily)
  Week 5  : Withdrawal - water only (unless disease present)
  Week 6  : Water only - holding for sale
"""

import sys
import os
import datetime
import random

from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext

from app.database import engine, SessionLocal, Base
from app.models.auth import User
from app.models.farm import Farm
from app.models.batch import Batch
from app.models.reading import FeedWaterReading
from app.models.growth import GrowthSample
from app.models.medication import MedicationEntry
from app.models.alert import Alert
from app.models.media import MediaClip, InferenceResult
from app.models.user_farm import UserFarmAssociation

# Must match the scheme configured in app/routers/auth.py
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Evans' weekly averages -> daily targets (200 birds)
# (feed_kg_per_day, water_litres_per_day)
# ---------------------------------------------------------------------------
WEEKLY_DAILY_TARGETS = {
    1: (5.0,   10.0),
    2: (7.5,   25.0),
    3: (20.0,  35.0),
    4: (30.0,  80.0),
    5: (40.0, 100.0),
    6: (50.0, 120.0),
}

# ---------------------------------------------------------------------------
# Evans' actual growth curve — midpoints of his observed weekly ranges
# Sample size: 30 birds (as Evans described — randomly picked)
# ---------------------------------------------------------------------------
GROWTH_CURVE = {
    7:  45,     # Week 1:  40 - 50 g
    14: 180,    # Week 2:  160 - 200 g
    21: 900,    # Week 3:  800 g - 1 kg
    28: 1400,   # Week 4:  1.3 - 1.5 kg
    35: 1800,   # Week 5:  1.7 - 1.9 kg
    42: 2250,   # Week 6:  2.0 - 2.5 kg
}

# ---------------------------------------------------------------------------
# Evans' REAL medication schedule (1-based day of batch)
# Vaccine dosage formula: (bird_count x day_age x 1.5) / 1000 = mL
# ---------------------------------------------------------------------------
MEDICATION_SCHEDULE = [
    # Week 1 — Stress Pack
    {
        "day": 1,
        "medicine_type": "Stress Pack",
        "dosage": "5 g (1 teaspoon) in 10 L water — daily throughout Week 1",
        "outcome_note": "Administered daily in Week 1 to reduce transport and placement stress.",
    },
    # Week 2 — Chickens Formula
    {
        "day": 8,
        "medicine_type": "Chickens Formula",
        "dosage": "10 g (1 tablespoon) in 20 L water — daily throughout Week 2",
        "outcome_note": "General health supplement administered throughout Week 2.",
    },
    # Day 10 — Gumboro (IBD) Vaccine
    {
        "day": 10,
        "medicine_type": "Gumboro (IBD) Vaccine",
        "dosage": "200 x 10 x 1.5 / 1000 = 3.0 mL added to 3 L drinking water",
        "outcome_note": "First Gumboro vaccination. Water withheld 1-2 hrs before administration.",
    },
    # Day 14 — Newcastle Vaccine
    {
        "day": 14,
        "medicine_type": "Newcastle Disease Vaccine",
        "dosage": "200 x 14 x 1.5 / 1000 = 4.2 mL added to 4 L drinking water",
        "outcome_note": "First Newcastle vaccination. Birds responding well.",
    },
    # Week 3 — Organic Mash Booster/Antibiotic
    {
        "day": 15,
        "medicine_type": "Organic Mash (Booster / Antibiotic)",
        "dosage": "3 tablespoons in 20 L water — daily throughout Week 3",
        "outcome_note": "Antibiotic booster applied throughout Week 3 to support immunity.",
    },
    # Day 18 — Gumboro Booster
    {
        "day": 18,
        "medicine_type": "Gumboro (IBD) Vaccine — Booster",
        "dosage": "200 x 18 x 1.5 / 1000 = 5.4 mL added to 5 L drinking water",
        "outcome_note": "Gumboro booster dose administered successfully.",
    },
    # Day 21 — Newcastle Booster
    {
        "day": 21,
        "medicine_type": "Newcastle Disease Vaccine — Booster",
        "dosage": "200 x 21 x 1.5 / 1000 = 6.3 mL added to 6 L drinking water",
        "outcome_note": "Newcastle booster administered. Birds showing good immunity response.",
    },
    # Week 4 — Organic Mash Booster/Antibiotic
    {
        "day": 22,
        "medicine_type": "Organic Mash (Booster / Antibiotic)",
        "dosage": "3 tablespoons in 20 L water — daily throughout Week 4",
        "outcome_note": "Continued antibiotic booster through Week 4 as precaution.",
    },
    # Week 5 — Withdrawal Period
    {
        "day": 29,
        "medicine_type": "Withdrawal Period — Water Only",
        "dosage": "Clean water only. No medication.",
        "outcome_note": (
            "Withdrawal week before sale. All medications cleared. "
            "If disease observed, continue Organic Mash."
        ),
    },
    # Week 6 — Holding for Sale
    {
        "day": 36,
        "medicine_type": "Holding for Sale — Water Only",
        "dosage": "Clean water only.",
        "outcome_note": "Birds on water only while awaiting sale. No medications administered.",
    },
]


def get_week(day_index):
    """Return the week number (1-6) for a 0-based day index."""
    return min((day_index // 7) + 1, 6)


def interpolate_daily(day_index, jitter_pct=0.07):
    """
    Return (feed_kg, water_litres) for a given day using Evans' weekly averages,
    with a smooth intra-week ramp and small random jitter.
    """
    week = get_week(day_index)
    base_feed, base_water = WEEKLY_DAILY_TARGETS[week]

    # Days earlier in the week are slightly below average, later days slightly above
    day_in_week = day_index % 7
    ramp = 0.93 + (day_in_week / 6) * 0.14   # 0.93 to 1.07

    feed  = base_feed  * ramp * random.uniform(1 - jitter_pct, 1 + jitter_pct)
    water = base_water * ramp * random.uniform(1 - jitter_pct, 1 + jitter_pct)
    return round(feed, 1), round(water, 1)


def build_readings(batch, days, start_date, anomaly_day=None):
    readings = []
    for i in range(days):
        date = start_date + datetime.timedelta(days=i)
        feed, water = interpolate_daily(i)
        flagged = False
        if anomaly_day is not None and i == anomaly_day:
            feed  = round(feed  * 0.55, 1)   # ~45% drop
            water = round(water * 0.60, 1)   # ~40% drop
            flagged = True
        readings.append(FeedWaterReading(
            batch_id=batch.id,
            date=date,
            feed_kg=feed,
            water_litres=water,
            flagged_abnormal=flagged,
        ))
    return readings


def build_growth_samples(batch, start_date, max_days):
    """
    Use Evans' actual weekly weight ranges (midpoints) with +/-15 g jitter.
    Sample size is 30 birds (as Evans described).
    """
    samples = []
    for day_offset, weight_g in GROWTH_CURVE.items():
        if day_offset > max_days:
            break
        samples.append(GrowthSample(
            batch_id=batch.id,
            date=start_date + datetime.timedelta(days=day_offset),
            avg_weight_g=round(weight_g + random.uniform(-15, 15), 1),
            sample_size=30,   # Evans randomly picks 30 birds
        ))
    return samples


def build_medications(batch, start_date, max_days):
    meds = []
    for entry in MEDICATION_SCHEDULE:
        if (entry["day"] - 1) > max_days:
            break
        meds.append(MedicationEntry(
            batch_id=batch.id,
            date=start_date + datetime.timedelta(days=entry["day"] - 1),
            medicine_type=entry["medicine_type"],
            dosage=entry["dosage"],
            outcome_note=entry["outcome_note"],
        ))
    return meds


def seed():
    random.seed(42)  # Reproducible output

    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # ── Clean slate ──────────────────────────────────────────────────────────
    db.query(InferenceResult).delete()
    db.query(MediaClip).delete()
    db.query(Alert).delete()
    db.query(MedicationEntry).delete()
    db.query(GrowthSample).delete()
    db.query(FeedWaterReading).delete()
    db.query(Batch).delete()
    db.query(UserFarmAssociation).delete()
    db.query(Farm).delete()
    db.query(User).delete()
    db.commit()

    print("Seeding database with Evans' real farm data...")

    # ── 0. Demo User ──────────────────────────────────────────────────────────
    # Hash is generated with sha256_crypt — matches app/routers/auth.py
    demo_user = User(
        username="evans",
        hashed_password=pwd_context.hash("agrisense2025"),
        full_name="Evans Mulenga",
    )
    db.add(demo_user)
    
    operator_user = User(
        username="operator",
        hashed_password=pwd_context.hash("prime_nest_2026"),
        full_name="Evans Kabwe"
    )
    db.add(operator_user)
    
    db.commit()
    db.refresh(demo_user)
    db.refresh(operator_user)

    # ── 1. Farm ───────────────────────────────────────────────────────────────
    farm = Farm(name="Prime Nest Poultry Farm", location="Lusaka, Zambia")
    db.add(farm)
    db.commit()
    db.refresh(farm)

    # Seed UserFarmAssociation
    assoc = UserFarmAssociation(user_id=demo_user.id, farm_id=farm.id, role="owner")
    assoc_operator = UserFarmAssociation(user_id=operator_user.id, farm_id=farm.id, role="owner")
    db.add(assoc)
    db.add(assoc_operator)
    db.commit()

    # ── 2. Batches ────────────────────────────────────────────────────────────
    today = datetime.date.today()
    active_start   = today - datetime.timedelta(days=21)   # Currently Day 22 of 42
    archived_start = today - datetime.timedelta(days=107)  # A completed cycle ~3 months ago

    batch_active = Batch(
        farm_id=farm.id,
        start_date=active_start,
        bird_count=200,
        breed="Cobb 500",
        status="active",
    )
    batch_archived = Batch(
        farm_id=farm.id,
        start_date=archived_start,
        bird_count=200,
        breed="Cobb 500",
        status="archived",
    )
    db.add_all([batch_active, batch_archived])
    db.commit()
    db.refresh(batch_active)
    db.refresh(batch_archived)

    # ── 3. Feed & Water Readings ──────────────────────────────────────────────
    # Active: 22 days logged, anomaly on Day 15 (consumption dip)
    # Archived: full 42 days, anomaly on Day 30
    db.add_all(build_readings(batch_active,   days=22, start_date=active_start,   anomaly_day=15))
    db.add_all(build_readings(batch_archived, days=42, start_date=archived_start, anomaly_day=30))
    db.commit()

    # ── 4. Growth Samples — Evans' real weekly weigh-ins, 30 birds ───────────
    db.add_all(build_growth_samples(batch_active,   active_start,   max_days=21))
    db.add_all(build_growth_samples(batch_archived, archived_start, max_days=42))
    db.commit()

    # ── 5. Medication Entries — Evans' real schedule ──────────────────────────
    db.add_all(build_medications(batch_active,   active_start,   max_days=21))
    db.add_all(build_medications(batch_archived, archived_start, max_days=42))
    db.commit()

    # ── 6. Alerts ─────────────────────────────────────────────────────────────
    db.add_all([
        Alert(
            batch_id=batch_active.id,
            type="feed_drop",
            message=(
                "Day 15: Feed consumption dropped ~45% (from ~17 kg to ~9 kg) "
                "and water intake dropped ~40%. Possible heat stress or early illness. "
                "Organic Mash antibiotic course started Day 15."
            ),
            severity="critical",
            acknowledged=True,
        ),
        Alert(
            batch_id=batch_active.id,
            type="growth_low",
            message=(
                "Week 3 average weight (~900 g) is tracking below the 1 kg+ target. "
                "Monitor closely — may be linked to Day 15 feed dip."
            ),
            severity="warning",
            acknowledged=False,
        ),
        Alert(
            batch_id=batch_active.id,
            type="water_high",
            message=(
                "Day 20: Water consumption is 8% above the weekly average. "
                "Check for leaking nipple drinkers or early signs of heat stress."
            ),
            severity="info",
            acknowledged=False,
        ),
    ])
    db.commit()

    # ── 7. Media Clip & Inference Result (placeholder for CV module) ──────────
    clip = MediaClip(
        batch_id=batch_active.id,
        file_url="/uploads/sample_coop_video.mp4",
        uploaded_at=datetime.datetime.now(),
    )
    db.add(clip)
    db.commit()
    db.refresh(clip)

    # Seed 196 tracked birds (1 is inactive, others active)
    mock_tracked_birds = []
    for tid in range(1, 197):
        if tid == 1:
            inactivity = 75  # > 60 seconds
            status = "inactive"
        else:
            inactivity = random.randint(0, 12)
            status = "active"
        mock_tracked_birds.append({
            "track_id": tid,
            "inactivity_duration_sec": inactivity,
            "status": status,
            "x": random.randint(50, 580),
            "y": random.randint(50, 420)
        })

    discrepancy_note = "4 bird(s) missing. Detected potential mortality (lethargic/dead bird detected in visual)."

    inference = InferenceResult(
        media_clip_id=clip.id,
        bird_count_est=196,
        movement_score=0.81,
        low_activity_windows=[
            {"start_sec": 8,  "end_sec": 22, "reason": "Birds clustered near feeder (morning feeding)"},
            {"start_sec": 45, "end_sec": 60, "reason": "Resting period — normal midday behaviour"},
        ],
        tracked_birds=mock_tracked_birds,
        discrepancy_note=discrepancy_note
    )
    db.add(inference)

    # Seed the corresponding Alert
    db.add(Alert(
        batch_id=batch_active.id,
        type="mortality",
        message="Visual anomaly: 4 bird(s) missing from expected flock. Lethargic/inactive bird detected in visual. Expected: 200, Detected: 196.",
        severity="critical",
        acknowledged=False,
        created_at=datetime.datetime.now()
    ))
    db.commit()
    db.close()

    print("\nDatabase seeded successfully!")
    print("  Login   : username=evans  |  password=agrisense2025")
    print("  Farm    : Prime Nest Poultry Farm, Lusaka, Zambia")
    print("  Batches : 1 active (Day 22 of 42) + 1 archived (full 42-day cycle)")
    print("  Birds   : 200 per batch — Evans' real data")
    print("  Feed    : ~1,068 kg over 42 days (approx 22 x 50 kg bags)")
    print("  Water   : 2,590 L over 42 days")
    print("  Growth  : Sample of 30 birds weekly (Evans' actual observed ranges)")
    print("  Meds    : 10 entries — Stress Pack, Chickens Formula, Gumboro x2,")
    print("            Newcastle x2, Organic Mash x2, Withdrawal, Holding")
    print("  Alerts  : 3 (1 critical, 1 warning, 1 info)")


if __name__ == "__main__":
    seed()
