import pytest

from app import app, members, workouts


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        members.clear()
        workouts.clear()
        yield client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Welcome to ACEest Fitness & Gym"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_get_members_empty(client):
    response = client.get("/members")

    assert response.status_code == 200
    assert response.get_json() == []


def test_add_member(client):
    response = client.post(
        "/members",
        json={"name": "John", "age": 25}
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 1
    assert data["name"] == "John"
    assert data["age"] == 25


def test_add_member_missing_data(client):
    response = client.post(
        "/members",
        json={"name": "John"}
    )

    assert response.status_code == 400


def test_add_member_invalid_age(client):
    response = client.post(
        "/members",
        json={"name": "John", "age": 150}
    )

    assert response.status_code == 400


def test_get_member(client):
    client.post(
        "/members",
        json={"name": "John", "age": 25}
    )

    response = client.get("/members/1")

    assert response.status_code == 200
    assert response.get_json()["name"] == "John"


def test_get_member_not_found(client):
    response = client.get("/members/999")

    assert response.status_code == 404


def test_delete_member(client):
    client.post(
        "/members",
        json={"name": "John", "age": 25}
    )

    response = client.delete("/members/1")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Member deleted successfully"

    response = client.get("/members/1")

    assert response.status_code == 404


def test_bmi_calculation(client):
    response = client.post(
        "/bmi",
        json={"weight": 70, "height": 1.75}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["bmi"] == 22.86
    assert data["category"] == "Normal weight"


def test_bmi_missing_data(client):
    response = client.post(
        "/bmi",
        json={"weight": 70}
    )

    assert response.status_code == 400


def test_bmi_invalid_values(client):
    response = client.post(
        "/bmi",
        json={"weight": 0, "height": 1.75}
    )

    assert response.status_code == 400


def test_bmi_underweight(client):
    response = client.post(
        "/bmi",
        json={"weight": 45, "height": 1.75}
    )

    assert response.status_code == 200
    assert response.get_json()["category"] == "Underweight"


def test_bmi_overweight(client):
    response = client.post(
        "/bmi",
        json={"weight": 85, "height": 1.75}
    )

    assert response.status_code == 200
    assert response.get_json()["category"] == "Overweight"


def test_add_workout(client):
    client.post(
        "/members",
        json={"name": "John", "age": 25}
    )

    response = client.post(
        "/workouts",
        json={
            "member_id": 1,
            "exercise": "Running",
            "duration": 30
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 1
    assert data["member_id"] == 1
    assert data["exercise"] == "Running"
    assert data["duration"] == 30


def test_add_workout_member_not_found(client):
    response = client.post(
        "/workouts",
        json={
            "member_id": 999,
            "exercise": "Running",
            "duration": 30
        }
    )

    assert response.status_code == 404


def test_add_workout_invalid_duration(client):
    client.post(
        "/members",
        json={"name": "John", "age": 25}
    )

    response = client.post(
        "/workouts",
        json={
            "member_id": 1,
            "exercise": "Running",
            "duration": 0
        }
    )

    assert response.status_code == 400


def test_get_workouts_empty(client):
    response = client.get("/workouts")

    assert response.status_code == 200
    assert response.get_json() == []
