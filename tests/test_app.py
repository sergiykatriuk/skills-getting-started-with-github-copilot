"""
Test file for the FastAPI application for Mergington High School activities.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to the static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_activity_structure():
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    activities = response.json()
    for activity_name, activity in activities.items():
        assert isinstance(activity, dict)
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    test_email = "test_student@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for Chess Club"

    # Verify the student was added
    activities = client.get("/activities").json()
    assert test_email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test that a student cannot sign up for the same activity twice"""
    test_email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response = client.post(f"/activities/Programming Class/signup?email={test_email}")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/Programming Class/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First, sign up a test student
    test_email = "unregister_test@mergington.edu"
    client.post(f"/activities/Art Club/signup?email={test_email}")
    
    # Then unregister them
    response = client.post(f"/activities/Art Club/unregister?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {test_email} from Art Club"
    
    # Verify the student was removed
    activities = client.get("/activities").json()
    assert test_email not in activities["Art Club"]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who is not registered"""
    response = client.post("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()