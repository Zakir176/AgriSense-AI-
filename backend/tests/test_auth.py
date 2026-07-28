from app.models.auth import User
from app.routers.auth import get_password_hash

def test_login_success(client, db_session):
    # Seed a test user
    test_user = User(
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User"
    )
    db_session.add(test_user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, db_session):
    test_user = User(
        username="testuser2",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User 2"
    )
    db_session.add(test_user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser2", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
