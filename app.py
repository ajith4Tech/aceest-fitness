from flask import Flask, jsonify, request

app = Flask(__name__)

members = []


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

    member = {
        "id": len(members) + 1,
        "name": name,
        "age": age
    }

    members.append(member)

    return jsonify(member), 201


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

    return jsonify({
        "bmi": round(bmi, 2)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
