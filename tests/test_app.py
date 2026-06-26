from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200

    unregister_response = client.delete("/activities/Chess Club/unregister?email=test@example.com")
    assert unregister_response.status_code == 200

    activities_response = client.get("/activities")
    activity = activities_response.json()["Chess Club"]
    assert "test@example.com" not in activity["participants"]


def test_activities_endpoint_disables_caching_for_live_updates():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")
