import pytest

from ACEest_Fitness import APP_VERSION, app, progress, reset_data


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        reset_data()
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

def test_member_ids_are_unique_after_delete(client):
    client.post("/members", json={"name": "John", "age": 25})
    client.post("/members", json={"name": "Mary", "age": 30})
    client.delete("/members/1")
    response = client.post("/members", json={"name": "Bob", "age": 40})
    assert response.get_json()["id"] == 3
    assert client.get("/members/2").get_json()["name"] == "Mary"

def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.get_json()["version"] == APP_VERSION

def test_list_programs(client):
    response = client.get("/programs")

    assert response.status_code == 200

    codes = [program["code"] for program in response.get_json()]

    assert codes == ["FL", "MG", "BG"]


def test_get_program_case_insensitive(client):
    response = client.get("/programs/fl")

    assert response.status_code == 200

    data = response.get_json()

    assert data["code"] == "FL"
    assert data["name"] == "Fat Loss"
    assert data["target_kcal"] == 2000
    assert len(data["workout"]) == 5


def test_get_program_not_found(client):
    response = client.get("/programs/XX")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Program not found"

def test_program_calories(client):
    response = client.get("/programs/FL/calories?weight=70")

    assert response.status_code == 200

    data = response.get_json()

    assert data["calorie_factor"] == 22
    assert data["daily_calories"] == 1540


def test_program_calories_lowercase_code(client):
    response = client.get("/programs/mg/calories?weight=80")

    assert response.status_code == 200
    assert response.get_json()["daily_calories"] == 2800


def test_program_calories_missing_weight(client):
    response = client.get("/programs/FL/calories")

    assert response.status_code == 400


def test_program_calories_invalid_weight(client):
    for weight in ["-5", "0", "abc", "500", "nan"]:
        response = client.get(f"/programs/FL/calories?weight={weight}")

        assert response.status_code == 400


def test_program_calories_unknown_program(client):
    response = client.get("/programs/XX/calories?weight=70")

    assert response.status_code == 404

def add_john(client):
    client.post("/members", json={"name": "John", "age": 25})


def test_add_progress(client):
    add_john(client)

    response = client.post(
        "/members/1/progress",
        json={"week": "2026-W48", "adherence": 80}
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "member_id": 1,
        "week": "2026-W48",
        "adherence": 80
    }


def test_progress_summary(client):
    add_john(client)
    client.post("/members/1/progress", json={"week": "2026-W49", "adherence": 90})
    client.post("/members/1/progress", json={"week": "2026-W48", "adherence": 70})

    response = client.get("/members/1/progress")

    assert response.status_code == 200

    data = response.get_json()

    assert data["weeks_logged"] == 2
    assert data["average_adherence"] == 80.0
    assert [entry["week"] for entry in data["entries"]] == ["2026-W48", "2026-W49"]


def test_progress_empty(client):
    add_john(client)

    data = client.get("/members/1/progress").get_json()

    assert data["weeks_logged"] == 0
    assert data["average_adherence"] is None


def test_progress_member_not_found(client):
    response = client.post(
        "/members/999/progress",
        json={"week": "2026-W48", "adherence": 80}
    )

    assert response.status_code == 404
    assert client.get("/members/999/progress").status_code == 404


def test_progress_invalid_input(client):
    add_john(client)

    invalid_bodies = [
        {"week": "48", "adherence": 80},
        {"week": "2026-W48", "adherence": 150},
        {"week": "2026-W48", "adherence": "80"},
        {"week": "2026-W48", "adherence": True},
        {"adherence": 80},
    ]

    for body in invalid_bodies:
        response = client.post("/members/1/progress", json=body)

        assert response.status_code == 400

    assert client.post("/members/1/progress").status_code == 400


def test_progress_duplicate_week(client):
    add_john(client)
    client.post("/members/1/progress", json={"week": "2026-W48", "adherence": 80})

    response = client.post(
        "/members/1/progress",
        json={"week": "2026-W48", "adherence": 60}
    )

    assert response.status_code == 409


def test_progress_removed_with_member(client):
    add_john(client)
    client.post("/members/1/progress", json={"week": "2026-W48", "adherence": 80})

    client.delete("/members/1")

    assert progress == []
