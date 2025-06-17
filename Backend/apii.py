from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance"]
collection = db["users"]
attendance_collection = db["attendance_records"]

# Home route
@app.route('/')
def home():
    return "Online Attendance System API is running"

# Signup route
@app.route('/signup', methods=['GET'])
def signup():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return jsonify({"status": "fail", "message": "Missing username or password"}), 400

    existing_user = collection.find_one({"username": username})
    if existing_user:
        return jsonify({"status": "fail", "message": "User already exists"}), 409

    collection.insert_one({"username": username, "password": password})
    return jsonify({"status": "success", "message": "User registered successfully"}), 200

# Login route
@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return jsonify({"status": "fail", "message": "Missing username or password"}), 400

    user = collection.find_one({"username": username, "password": password})
    if user:
        return jsonify({"status": "success", "message": "Login successful"}), 200
    else:
        return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

# Save attendance route
@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    data = request.get_json()

    required_fields = {'username', 'date', 'attendance', 'present_count', 'absent_count'}
    if not data or not required_fields.issubset(data):
        return jsonify({"status": "fail", "message": "Invalid data format"}), 400

    # Optional: Check if attendance for the date already exists
    existing = attendance_collection.find_one({
        "username": data["username"],
        "date": data["date"]
    })
    if existing:
        return jsonify({"status": "fail", "message": "Attendance already submitted for today"}), 409

    attendance_collection.insert_one(data)
    return jsonify({"status": "success", "message": "Attendance saved successfully"}), 200

# Get attendance records (with optional date/month filter)
@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    username = request.args.get('username')
    date_filter = request.args.get('date')
    month_filter = request.args.get('month')

    if not username:
        return jsonify({"status": "fail", "message": "Missing username"}), 400

    query = {"username": username}

    if date_filter:
        query["date"] = date_filter
    elif month_filter:
        # Use regex to match the beginning of the date field with the given month (YYYY-MM)
        query["date"] = {"$regex": f"^{month_filter}"}

    records = list(attendance_collection.find(query, {"_id": 0}))  # exclude _id
    return jsonify({"status": "success", "records": records}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)
