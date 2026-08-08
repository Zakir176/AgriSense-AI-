import pytest
from datetime import date
from app.models.auth import User
from app.routers.auth import get_password_hash

def get_auth_token(client, db_session, username="inventory_owner"):
    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            hashed_password=get_password_hash("testpassword"),
            full_name="Inventory Owner"
        )
        db_session.add(user)
        db_session.commit()

    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_inventory_adjustment_creation_and_summary(client, db_session):
    token = get_auth_token(client, db_session)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a farm and batch
    farm_resp = client.post("/api/v1/farms", headers=headers, json={"name": "Inventory Test Farm", "location": "Test Loc"})
    assert farm_resp.status_code == 201
    farm_id = farm_resp.json()["id"]

    batch_resp = client.post("/api/v1/batches", headers=headers, json={
        "farm_id": farm_id,
        "start_date": str(date.today()),
        "bird_count": 200,
        "breed": "Cobb 500"
    })
    assert batch_resp.status_code == 201
    batch_id = batch_resp.json()["id"]

    # 2. Check initial inventory summary
    sum_resp = client.get(f"/api/v1/inventory/batch/{batch_id}/summary", headers=headers)
    assert sum_resp.status_code == 200
    data = sum_resp.json()
    assert data["initial_bird_count"] == 200
    assert data["current_live_count"] == 200
    assert data["total_mortality"] == 0

    # 3. Create a daily reading with mortality
    reading_resp = client.post("/api/v1/readings", headers=headers, json={
        "batch_id": batch_id,
        "date": str(date.today()),
        "feed_kg": 5.0,
        "water_litres": 10.0,
        "mortality_count": 3
    })
    assert reading_resp.status_code == 201

    # Verify inventory auto-sync
    sum_resp2 = client.get(f"/api/v1/inventory/batch/{batch_id}/summary", headers=headers)
    assert sum_resp2.status_code == 200
    data2 = sum_resp2.json()
    assert data2["total_mortality"] == 3
    assert data2["current_live_count"] == 197
    assert len(data2["history"]) == 1
    assert data2["history"][0]["source"] == "daily_reading"

    # 4. Record manual inventory sale
    sale_resp = client.post(f"/api/v1/inventory/batch/{batch_id}", headers=headers, json={
        "date": str(date.today()),
        "adjustment_type": "sale",
        "quantity_delta": 20,
        "notes": "Sold to local market"
    })
    assert sale_resp.status_code == 201

    # Verify updated live count
    sum_resp3 = client.get(f"/api/v1/inventory/batch/{batch_id}/summary", headers=headers)
    assert sum_resp3.status_code == 200
    data3 = sum_resp3.json()
    assert data3["total_mortality"] == 3
    assert data3["total_sales"] == 20
    assert data3["current_live_count"] == 177
    assert len(data3["history"]) == 2
