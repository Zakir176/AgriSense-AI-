from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.reading import FeedWaterReading
from ..models.alert import Alert

def check_reading_anomalies(db: Session, batch_id: int, reading_date: date, feed_kg: float, water_litres: float) -> bool:
    """
    Computes 7-day rolling average for the batch prior to the reading_date.
    If the current reading deviates from the average by more than 20%,
    flag it as abnormal and trigger a system Alert.
    Returns True if flagged abnormal, False otherwise.
    """
    # Fetch readings from the last 7 days prior to reading_date
    start_date = reading_date - timedelta(days=7)
    end_date = reading_date - timedelta(days=1)
    
    prev_readings = db.query(FeedWaterReading).filter(
        FeedWaterReading.batch_id == batch_id,
        FeedWaterReading.date >= start_date,
        FeedWaterReading.date <= end_date
    ).all()
    
    if len(prev_readings) < 3:
        # Not enough data points to establish a rolling average baseline (require at least 3 points)
        return False
        
    avg_feed = sum(r.feed_kg for r in prev_readings) / len(prev_readings)
    avg_water = sum(r.water_litres for r in prev_readings) / len(prev_readings)
    
    flagged = False
    messages = []
    
    # 20% deviation check
    if avg_feed > 0:
        feed_dev = abs(feed_kg - avg_feed) / avg_feed
        if feed_dev > 0.20:
            flagged = True
            direction = "dropped" if feed_kg < avg_feed else "increased"
            messages.append(f"Feed consumption {direction} by {feed_dev:.1%} (Current: {feed_kg}kg vs 7d avg: {avg_feed:.1f}kg)")
            
    if avg_water > 0:
        water_dev = abs(water_litres - avg_water) / avg_water
        if water_dev > 0.20:
            flagged = True
            direction = "dropped" if water_litres < avg_water else "increased"
            messages.append(f"Water consumption {direction} by {water_dev:.1%} (Current: {water_litres}L vs 7d avg: {avg_water:.1f}L)")
            
    if flagged:
        # Trigger an alert
        alert_msg = " | ".join(messages)
        db_alert = Alert(
            batch_id=batch_id,
            type="feed_water_anomaly",
            message=alert_msg,
            severity="warning",
            acknowledged=False
        )
        db.add(db_alert)
        # Flush alert so it gets id but is committed with the reading
        db.flush()
        
    return flagged
