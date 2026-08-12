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
from app.models.scheduled_treatment import ScheduledTreatment

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


# ---------------------------------------------------------------------------
# Temperature profile — realistic barn ambient temps across a 6-week cycle
# Week 1-2: 30-33°C (brooder heat lamps), Week 3-4: 27-30°C, Week 5-6: 24-28°C
# ---------------------------------------------------------------------------
WEEKLY_TEMP_RANGES = {
    1: (30.0, 33.0),
    2: (29.5, 32.5),
    3: (27.0, 30.0),
    4: (26.5, 29.5),
    5: (24.5, 28.0),
    6: (24.0, 27.5),
}


def get_daily_temperature(day_index):
    """Return a realistic barn temperature for a given day."""
    week = get_week(day_index)
    lo, hi = WEEKLY_TEMP_RANGES[week]
    return round(random.uniform(lo, hi), 1)


def build_readings(batch, days, start_date, anomaly_day=None):
    readings = []
    for i in range(days):
        date = start_date + datetime.timedelta(days=i)
        feed, water = interpolate_daily(i)
        temp = get_daily_temperature(i)
        flagged = False
        if anomaly_day is not None and i == anomaly_day:
            feed  = round(feed  * 0.55, 1)   # ~45% drop
            water = round(water * 0.60, 1)   # ~40% drop
            temp  = round(temp + 3.5, 1)     # Heat stress spike on anomaly day
            flagged = True
        readings.append(FeedWaterReading(
            batch_id=batch.id,
            date=date,
            feed_kg=feed,
            water_litres=water,
            flagged_abnormal=flagged,
            temperature_celsius=temp,
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

    Base.metadata.drop_all(bind=engine)
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

    # ── 5. Medication Entries & Scheduled Treatments ─────────────────────────
    db.add_all(build_medications(batch_active,   active_start,   max_days=21))
    db.add_all(build_medications(batch_archived, archived_start, max_days=42))
    db.commit()

    # Scheduled Treatments with Prescribers & Digital Sign-offs
    db.add_all([
        ScheduledTreatment(
            batch_id=batch_active.id,
            title="Gumboro (IBD) Vaccine - Primary",
            treatment_type="vaccine",
            scheduled_date=active_start + datetime.timedelta(days=9),
            dosage="3.0 mL in 3 L drinking water",
            notes="Administered via drinking water after 2-hour water withholding.",
            status="completed",
            completed_date=active_start + datetime.timedelta(days=9),
            prescribed_by="Dr. Sarah Jenkins (Veterinarian)",
            administered_by="Evans Kabwe (Farmhand)",
            digital_signature="SIG-AGRI-GUMBORO-001",
            reminder_channel="browser"
        ),
        ScheduledTreatment(
            batch_id=batch_active.id,
            title="Newcastle Disease Vaccine - Primary",
            treatment_type="vaccine",
            scheduled_date=active_start + datetime.timedelta(days=13),
            dosage="4.2 mL in 4 L drinking water",
            notes="First Newcastle vaccination. Ensure cold water supply.",
            status="completed",
            completed_date=active_start + datetime.timedelta(days=13),
            prescribed_by="Dr. Sarah Jenkins (Veterinarian)",
            administered_by="Evans Kabwe (Farmhand)",
            digital_signature="SIG-AGRI-NEWCASTLE-001",
            reminder_channel="browser"
        ),
        ScheduledTreatment(
            batch_id=batch_active.id,
            title="Gumboro (IBD) Vaccine - Booster",
            treatment_type="vaccine",
            scheduled_date=active_start + datetime.timedelta(days=17),
            dosage="5.4 mL in 5 L drinking water",
            notes="Booster dose administered successfully.",
            status="completed",
            completed_date=active_start + datetime.timedelta(days=17),
            prescribed_by="Dr. Sarah Jenkins (Veterinarian)",
            administered_by="Evans Kabwe (Farmhand)",
            digital_signature="SIG-AGRI-GUMBORO-002",
            reminder_channel="browser"
        ),
        ScheduledTreatment(
            batch_id=batch_active.id,
            title="Newcastle Disease Vaccine - Booster",
            treatment_type="vaccine",
            scheduled_date=today, # Due Today / Overdue signoff
            dosage="6.3 mL in 6 L drinking water",
            notes="Ensure 2-hour water withholding prior to administration. Check flock condition.",
            status="pending",
            prescribed_by="Dr. Sarah Jenkins (Veterinarian)",
            reminder_channel="browser"
        ),
        ScheduledTreatment(
            batch_id=batch_active.id,
            title="Organic Mash Antibiotic Booster Course",
            treatment_type="medication",
            scheduled_date=today + datetime.timedelta(days=3),
            dosage="3 tablespoons in 20 L drinking water",
            notes="Weekly preventive antibiotic booster to support immunity.",
            status="pending",
            prescribed_by="Dr. Sarah Jenkins (Veterinarian)",
            reminder_channel="sms",
            phone_number="+260971234567"
        ),
        ScheduledTreatment(
            batch_id=batch_active.id,
            title="Coccidiosis & Vitamin Booster",
            treatment_type="supplement",
            scheduled_date=today + datetime.timedelta(days=7),
            dosage="10 g in 20 L water",
            notes="Pre-slaughter health booster and gut health support.",
            status="pending",
            prescribed_by="Dr. Sarah Jenkins (Veterinarian)",
            reminder_channel="both",
            phone_number="+260971234567"
        )
    ])
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

    # ── 7. Media Clips & Inference Results — multiple snapshots for trends ──
    # Create inference snapshots across multiple days so the Spatial Health
    # Trends chart has enough data points to render meaningful lines.

    # Clustering density naturally increases as birds grow larger and the
    # coop gets more crowded. We simulate a realistic upward trend.
    SNAPSHOT_SCHEDULE = [
        # (day_offset, clustering_density_pct, spatial_dispersion_index, bird_count_est)
        (2,   18.3, 72.1, 200),
        (5,   24.7, 65.4, 200),
        (8,   35.2, 58.8, 199),
        (10,  42.6, 52.3, 199),
        (13,  51.8, 47.1, 198),
        (15,  58.4, 43.5, 198),   # Anomaly day — heat stress spike
        (18,  63.1, 41.9, 197),
        (20,  68.5, 38.6, 196),
        (21,  71.2, 36.2, 196),   # Today's latest snapshot
    ]

    def build_mock_tracked_birds(count, day_offset):
        """Generate a compact set of tracked birds for a given snapshot."""
        birds = []
        for tid in range(1, count + 1):
            is_inactive = tid == 1 and day_offset >= 18
            inactivity = 75 if is_inactive else random.randint(0, 12)
            status = "inactive" if is_inactive else "active"
            base_x = random.randint(50, 580)
            base_y = random.randint(50, 420)
            timeline = []
            cx, cy = base_x, base_y
            for f in range(0, 150, 3):
                if is_inactive:
                    cx += random.choice([-1, 0, 1])
                    cy += random.choice([-1, 0, 1])
                else:
                    cx += random.randint(-4, 4)
                    cy += random.randint(-4, 4)
                cx = max(50, min(580, cx))
                cy = max(50, min(420, cy))
                timeline.append({"sec": round(f / 30.0, 2), "x": cx, "y": cy})
            birds.append({
                "track_id": tid,
                "inactivity_duration_sec": inactivity,
                "status": status,
                "x": base_x, "y": base_y,
                "history": timeline
            })
        return birds

    for day_offset, clust_pct, disp_idx, bird_est in SNAPSHOT_SCHEDULE:
        clip_date = active_start + datetime.timedelta(days=day_offset)
        clip = MediaClip(
            batch_id=batch_active.id,
            file_url=f"/uploads/coop_day{day_offset}.mp4",
            uploaded_at=datetime.datetime.combine(clip_date, datetime.time(10, 0)),
        )
        db.add(clip)
        db.flush()

        missing = 200 - bird_est
        if missing > 0:
            disc_note = f"{missing} bird(s) missing. Detected potential mortality."
        else:
            disc_note = f"Flock count match. Expected & Detected: {bird_est}."

        tracked = build_mock_tracked_birds(bird_est, day_offset)

        inference = InferenceResult(
            media_clip_id=clip.id,
            bird_count_est=bird_est,
            movement_score=round(random.uniform(0.65, 0.92), 2),
            low_activity_windows=[
                {"start_sec": 8, "end_sec": 22, "reason": "Birds clustered near feeder"},
                {"start_sec": 45, "end_sec": 60, "reason": "Resting period"},
            ],
            tracked_birds=tracked,
            discrepancy_note=disc_note,
            clustering_density_pct=clust_pct,
            spatial_dispersion_index=disp_idx,
        )
        db.add(inference)

    # Seed the corresponding Alert for the latest snapshot
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
