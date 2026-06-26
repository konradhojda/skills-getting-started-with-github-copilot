import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_seeded_activities_and_disables_caching(client):
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Science Club"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")
    payload = response.json()
    assert expected_activity_names.issubset(payload.keys())


def test_signup_for_activity_adds_student_to_participants(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_bad_request(client):
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert app_module.activities[activity_name]["participants"].count(email) == 1


def test_unregister_participant_removes_student_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "remove.me@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]
