from fastapi.testclient import TestClient
from src.app import app, activities
import pytest

client = TestClient(app)

def test_root_redirect():
    # Arrange: TestClient is set up
    # Act: Request the root endpoint
    response = client.get("/")
    # Assert: Should return 200 or redirect to /static/index.html
    assert response.status_code in (200, 307, 302)
    if response.status_code in (307, 302):
        assert "/static/index.html" in response.headers.get("location", "")
    else:
        # If not a redirect, should contain the static HTML content
        assert "<html" in response.text.lower() or "mergington" in response.text.lower()

def test_get_activities():
    # Arrange: TestClient is set up
    # Act: Request the activities endpoint
    response = client.get("/activities")
    # Assert: Should return all activities
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_success():
    # Arrange: Use a unique email for signup
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act: Post to signup endpoint
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: Should succeed
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json().get("message", "")
    # Cleanup: Remove the test email
    activities[activity]["participants"].remove(email)

def test_signup_activity_not_found():
    # Arrange: Use a non-existent activity
    activity = "NonExistentClub"
    email = "student@mergington.edu"
    # Act: Post to signup endpoint
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: Should return 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_already_signed_up():
    # Arrange: Use an email already signed up
    activity = "Chess Club"
    email = "michael@mergington.edu"
    # Act: Post to signup endpoint
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert: Should return 400
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
