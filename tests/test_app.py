"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    initial_state = {
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for competitions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["james@mergington.edu", "lucy@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with practices and games",
            "schedule": "Tuesdays, Wednesdays, Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and friendly matches",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu", "tyler@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in school plays and theatrical productions",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["natasha@mergington.edu", "ryan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art creation",
            "schedule": "Wednesdays and Saturdays, 2:00 PM - 4:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestRoot:
    """Tests for root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Debate Team" in data
        assert "Robotics Club" in data
        assert len(data) == 9
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Debate Team"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_activities_have_participants(self, client, reset_activities):
        """Test that some activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Debate Team"]["participants"]
        assert len(data["Robotics Club"]["participants"]) == 2


class TestSignup:
    """Tests for signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate(self, client, reset_activities):
        """Test that duplicate signup is prevented"""
        response = client.post("/activities/Debate Team/signup?email=alex@mergington.edu")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"
    
    def test_signup_increments_participants(self, client, reset_activities):
        """Test that signup increments participant count"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Tennis Club"]["participants"])
        
        client.post("/activities/Tennis Club/signup?email=newplayer@mergington.edu")
        
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Tennis Club"]["participants"])
        
        assert updated_count == initial_count + 1


class TestUnregister:
    """Tests for unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successfully unregistering from an activity"""
        response = client.post("/activities/Debate Team/unregister?email=alex@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Debate Team"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering when not registered returns 400"""
        response = client.post("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"
    
    def test_unregister_decrements_participants(self, client, reset_activities):
        """Test that unregister decrements participant count"""
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Robotics Club"]["participants"])
        
        client.post("/activities/Robotics Club/unregister?email=james@mergington.edu")
        
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Robotics Club"]["participants"])
        
        assert updated_count == initial_count - 1


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flow"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up then unregistering"""
        email = "flowtest@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        check_response = client.get("/activities")
        assert email in check_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]
    
    def test_multiple_signups(self, client, reset_activities):
        """Test multiple students signing up for same activity"""
        activity = "Art Studio"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        check_response = client.get("/activities")
        participants = check_response.json()[activity]["participants"]
        
        for email in emails:
            assert email in participants
