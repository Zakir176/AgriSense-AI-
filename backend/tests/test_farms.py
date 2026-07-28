from app.models.auth import User
from app.routers.auth import get_password_hash

def get_auth_token(client, db_session, username="farm_owner"):
    # Create user if it doesn't exist in the test DB
    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            hashed_password=get_password_hash("testpassword"),
            full_name="Farm Owner"
        )
        db_session.add(user)
        db_session.commit()

    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_create_farm(client, db_session):
    token = get_auth_token(client, db_session)
    
    response = client.post(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Farm", "location": "Test Location"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Farm"
    assert data["location"] == "Test Location"
    assert data["role"] == "owner"

def test_list_farms(client, db_session):
    token = get_auth_token(client, db_session)
    
    # Create a farm first
    client.post(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Farm 2", "location": "Test Location 2"}
    )
    
    # List farms
    response = client.get(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[-1]["name"] == "Test Farm 2"
