import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function():
    # keep a copy of original activities to restore between tests
    setup_function._orig = copy.deepcopy(activities)


def teardown_function():
    activities.clear()
    activities.update(setup_function._orig)


def test_get_activities():
    # Arrange
    expected = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected in data
    assert "participants" in data[expected]


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "testuser@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate_400():
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already present in seed data

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_remove_participant_success():
    # Arrange
    activity = "Chess Club"
    email = "daniel@mergington.edu"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_remove_missing_participant_404():
    # Arrange
    activity = "Chess Club"
    email = "nonexistent@example.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
