"""Backend tests for FastAPI school activities API.

Tests follow Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and preconditions
- Act: Perform a single API call
- Assert: Validate response status, data, and state changes
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Capture pristine activities state at module load time
_PRISTINE_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def client():
    """Fixture to provide TestClient for API testing."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities state before and after each test to ensure isolation.
    
    This fixture ensures that each test starts with a clean slate and does not
    affect subsequent tests, preventing test ordering dependencies.
    """
    activities.clear()
    activities.update(deepcopy(_PRISTINE_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(_PRISTINE_ACTIVITIES))


def test_get_activities(client):
    """Test retrieving all activities.
    
    Arrange: No setup needed beyond pristine state.
    Act: GET /activities
    Assert: 200 response with all activities present.
    """
    # Arrange
    expected_activity_count = 9

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities_data = response.json()
    assert len(activities_data) == expected_activity_count
    assert "Chess Club" in activities_data
    assert "Programming Class" in activities_data
    assert "participants" in activities_data["Chess Club"]
    assert isinstance(activities_data["Chess Club"]["participants"], list)


def test_signup_for_activity(client):
    """Test signing up a new student for an activity.
    
    Arrange: Select an activity and a new email not currently registered.
    Act: POST /activities/{activity_name}/signup
    Assert: 200 response and participant added to activity.
    """
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert new_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count + 1


def test_unregister_from_activity(client):
    """Test unregistering a student from an activity.
    
    Arrange: Select an activity and an existing participant.
    Act: DELETE /activities/{activity_name}/signup
    Assert: 200 response and participant removed from activity.
    """
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert existing_email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1
