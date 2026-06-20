from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "test.user+signup@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    encoded_email = quote(email, safe="")
    url = f"/activities/{encoded_activity}/signup?email={encoded_email}"

    # Act
    response = client.post(url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_removes_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "test.user+unregister@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    encoded_email = quote(email, safe="")
    signup_url = f"/activities/{encoded_activity}/signup?email={encoded_email}"
    delete_url = f"/activities/{encoded_activity}/participants?email={encoded_email}"

    client.post(signup_url)

    # Act
    response = client.delete(delete_url)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]
