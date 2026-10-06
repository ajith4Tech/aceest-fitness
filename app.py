from flask import Flask, jsonify, request

app = Flask(__name__)

members = []
workouts = []


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to ACEest Fitness & Gym"
    })


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
        "id": len(members) + 1,
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
        "id": len(workouts) + 1,
        "member_id": member_id,
        "exercise": exercise,
        "duration": duration
    }

    workouts.append(workout)

    return jsonify(workout), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
