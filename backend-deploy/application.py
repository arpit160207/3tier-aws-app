from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
import datetime

# Elastic Beanstalk looks for 'application' by default
application = Flask(__name__)
CORS(application)

# ── Config from Environment Variables (set in EB Console) ──
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/myapp")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
application.config["SECRET_KEY"] = SECRET_KEY

# ── MongoDB Connection ──
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_database("myapp")
    users_collection = db["users"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None


# ── Helper: Generate JWT Token ──
def generate_token(user_id, email):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# ── Routes ──

@application.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "3-Tier AWS App - Backend API",
        "version": "1.0.0"
    }), 200


@application.route("/health", methods=["GET"])
def health():
    """EB Health Check Endpoint"""
    return jsonify({"status": "healthy"}), 200


@application.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # Check if email already exists
        if users_collection.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 409

        # Hash password and save
        hashed_pw = generate_password_hash(password)
        user = {
            "name": name,
            "email": email,
            "password": hashed_pw,
            "created_at": datetime.datetime.utcnow()
        }
        result = users_collection.insert_one(user)
        token = generate_token(result.inserted_id, email)

        return jsonify({
            "message": "Registration successful",
            "token": token,
            "user": {"name": name, "email": email}
        }), 201

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@application.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = users_collection.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        token = generate_token(user["_id"], email)
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {"name": user["name"], "email": email}
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@application.route("/api/dashboard", methods=["GET"])
def dashboard():
    """Protected dashboard data endpoint"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization token required"}), 401

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        total_users = users_collection.count_documents({})
        return jsonify({
            "message": "Dashboard data fetched successfully",
            "user": payload["email"],
            "stats": {
                "total_users": total_users,
                "app_version": "1.0.0",
                "environment": os.environ.get("APP_ENV", "production"),
                "database": "MongoDB Atlas"
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=False)
