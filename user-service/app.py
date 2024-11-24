from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from bson import ObjectId
import jwt
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS with credentials support
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# --- Updated: Use environment variables ---
MONGO_URI = os.getenv("MONGO_URI")  # MongoDB connection string
SECRET_KEY = os.getenv("SECRET_KEY")  # JWT secret key

# Print to verify environment variables are loaded correctly
print("Mongo URI:", MONGO_URI)
print("Secret Key:", SECRET_KEY)

# MongoDB connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['user_db']

# Function to convert MongoDB ObjectId to string
def object_id_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# --- User Authentication ---
# Function to generate JWT token
def generate_token(user_id):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {
        'user_id': str(user_id),
        'exp': expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Function to verify JWT token and get user ID
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/')
def home():
    return "Hello, Flask!"

# --- Regular User Registration and Login ---
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if not data.get('username') or not data.get('password') or not data.get('sex') or not data.get('occupation'):
            return jsonify({"error": "Username, password, sex, and occupation are required"}), 400

        # Check if the user already exists
        if db.users.find_one({"username": data['username']}):
            return jsonify({"error": "User already exists"}), 400

        # Insert the new user with sex and occupation
        db.users.insert_one({
            "username": data['username'],
            "password": generate_password_hash(data['password']),
            "sex": data['sex'],
            "occupation": data['occupation']
        })
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the registration"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = db.users.find_one({"username": username})
        if not user:
            return jsonify({"error": "Invalid username or password"}), 400

        if not check_password_hash(user['password'], password):
            return jsonify({"error": "Invalid username or password"}), 400

        # Generate JWT token
        token = generate_token(user['_id'])
        return jsonify({"message": "Login successful", "token": token}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the login"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
