import os
from itertools import count

from flask import Flask, jsonify, request

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.2.0")

PROGRAMS = {
    "FL": {
        "name": "Fat Loss",
        "workout": [
            "Mon: 5x5 Back Squat + AMRAP",
            "Tue: EMOM 20min Assault Bike",
            "Wed: Bench Press + 21-15-9",
            "Thu: 10RFT Deadlifts/Box Jumps",
            "Fri: 30min Active Recovery",
        ],
        "diet": [
            "Breakfast: 3 Egg Whites + Oats Idli",
            "Lunch: Grilled Chicken + Brown Rice",
            "Dinner: Fish Curry + Millet Roti",
        ],
        "target_kcal": 2000,
	"calorie_factor":22,
    },
    "MG": {
        "name": "Muscle Gain",
        "workout": [
            "Mon: Squat 5x5",
            "Tue: Bench 5x5",
            "Wed: Deadlift 4x6",
            "Thu: Front Squat 4x8",
            "Fri: Incline Press 4x10",
            "Sat: Barbell Rows 4x10",
        ],
        "diet": [
            "Breakfast: 4 Eggs + PB Oats",
            "Lunch: Chicken Biryani (250g Chicken)",
            "Dinner: Mutton Curry + Jeera Rice",
        ],
        "target_kcal": 3200,
	"calorie_factor":35,
    },
    "BG": {
        "name": "Beginner",
        "workout": [
            "Circuit Training: Air Squats, Ring Rows, Push-ups",
            "Focus: Technique Mastery & Form",
        ],
        "diet": [
            "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati",
            "Protein: 120g/day",
        ],
        "target_kcal": 2200,
	"calorie_factor":26,
    },
}

members = []
workouts = []
_member_ids = count(1)
_workout_ids = count(1)

def reset_data():
    global _member_ids, _workout_ids
    members.clear()
    workouts.clear()
    _member_ids = count(1)
    _workout_ids = count(1)


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to ACEest Fitness & Gym"
    })

@app.route("/version")
def version():
   return jsonify({"version":APP_VERSION})

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/members", methods=["GET"])
def get_members():
    return jsonify(members)


@app.route("/members", methods=["POST"])
def add_member():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    name = data.get("name")
    age = data.get("age")

    if not name or age is None:
        return jsonify({
            "error": "Name and age are required"
        }), 400

    if not isinstance(age, int) or age <= 0 or age > 120:
        return jsonify({
            "error": "Age must be an integer between 1 and 120"
        }), 400

    member = {
        "id": next(_member_ids),
        "name": name,
        "age": age
    }

    members.append(member)

    return jsonify(member), 201


@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = next(
        (member for member in members if member["id"] == member_id),
        None
    )

    if not member:
        return jsonify({
            "error": "Member not found"
        }), 404

    return jsonify(member)


@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = next(
        (member for member in members if member["id"] == member_id),
        None
    )

    if not member:
        return jsonify({
            "error": "Member not found"
        }), 404

    members.remove(member)

    return jsonify({
        "message": "Member deleted successfully"
    })


@app.route("/bmi", methods=["POST"])
def calculate_bmi():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    weight = data.get("weight")
    height = data.get("height")

    if weight is None or height is None:
        return jsonify({
            "error": "Weight and height are required"
        }), 400

    if weight <= 0 or height <= 0:
        return jsonify({
            "error": "Weight and height must be greater than zero"
        }), 400

    bmi = weight / (height * height)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return jsonify({
        "bmi": round(bmi, 2),
        "category": category
    })


@app.route("/workouts", methods=["GET"])
def get_workouts():
    return jsonify(workouts)


@app.route("/workouts", methods=["POST"])
def add_workout():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    member_id = data.get("member_id")
    exercise = data.get("exercise")
    duration = data.get("duration")

    if member_id is None or not exercise or duration is None:
        return jsonify({
            "error": "Member ID, exercise and duration are required"
        }), 400

    if not isinstance(member_id, int) or member_id <= 0:
        return jsonify({
            "error": "Member ID must be a positive integer"
        }), 400

    if not isinstance(duration, (int, float)) or duration <= 0:
        return jsonify({
            "error": "Duration must be greater than zero"
        }), 400

    member = next(
        (member for member in members if member["id"] == member_id),
        None
    )

    if not member:
        return jsonify({
            "error": "Member not found"
        }), 404

    workout = {
        "id": next(_workout_ids),
        "member_id": member_id,
        "exercise": exercise,
        "duration": duration
    }

    workouts.append(workout)

    return jsonify(workout), 201

@app.route("/programs", methods=["GET"])
def list_programs():
    return jsonify([
        {"code": code, "name": program["name"]}
        for code, program in PROGRAMS.items()
    ])


@app.route("/programs/<code>", methods=["GET"])
def get_program(code):
    program = PROGRAMS.get(code.upper())

    if not program:
        return jsonify({
            "error": "Program not found"
        }), 404

    return jsonify({"code": code.upper(), **program})


@app.route("/programs/<code>/calories", methods=["GET"])
def program_calories(code):
    program = PROGRAMS.get(code.upper())

    if not program:
        return jsonify({
            "error": "Program not found"
        }), 404

    weight = request.args.get("weight", type=float)

    if weight is None or not 0 < weight <= 400:
        return jsonify({
            "error": "Weight must be a number between 0 and 400 kg"
        }), 400

    return jsonify({
        "program": code.upper(),
        "weight": weight,
        "calorie_factor": program["calorie_factor"],
        "daily_calories": int(weight * program["calorie_factor"])
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

