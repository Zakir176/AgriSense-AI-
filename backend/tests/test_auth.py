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

def test_register_public(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newfarmer",
            "password": "strongpassword123",
            "full_name": "New Farmer"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newfarmer"
    assert data["full_name"] == "New Farmer"

def test_login_json(client, db_session):
    test_user = User(
        username="jsonuser",
        hashed_password=get_password_hash("jsonpassword123"),
        full_name="JSON User"
    )
    db_session.add(test_user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/token",
        json={"username": "jsonuser", "password": "jsonpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

