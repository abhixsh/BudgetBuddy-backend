from flask import Flask, request, jsonify, make_response
from flask_cors import CORS  # Import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for specific routes (for admin)
CORS(app, origins="http://localhost:5173", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Connect to MongoDB using the URI from .env file
client = MongoClient(os.getenv("MONGO_URI"))
db = client.expense_manager  # Database name
users_collection = db.users  # Collection name for users

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Helper function to check password
def check_password(stored_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password)

# User Registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Check if user already exists
    if users_collection.find_one({"username": username}):
        return jsonify({"message": "Username already taken"}), 400

    hashed_password = hash_password(password)

    new_user = {
        "username": username,
        "password": hashed_password,
        "role": "user"  # Default role is 'user'
    }

    users_collection.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = users_collection.find_one({"username": username})

    if not user or not check_password(user["password"], password):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200

# Admin Registration
@app.route('/admin/register', methods=['POST'])
def register_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "Username already taken"}), 400

    hashed_password = hash_password(password)

    new_admin = {
        "username": username,
        "password": hashed_password,
        "role": "admin"
    }

    users_collection.insert_one(new_admin)
    return jsonify({"message": "Admin registered successfully"}), 201

# Admin Login
@app.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    admin = users_collection.find_one({"username": username, "role": "admin"})

    if not admin or not check_password(admin["password"], password):
        return jsonify({"message": "Invalid admin credentials"}), 401

    return jsonify({"message": "Admin login successful"}), 200

# Admin CRUD - Get All Users and Admins
@app.route('/admin/users', methods=['GET'])
def get_users_and_admins():
    try:
        admin_username = request.headers.get('admin_username')
        admin_password = request.headers.get('admin_password')
        # Admin authentication
        admin_authenticate(admin_username, admin_password)

        users = users_collection.find()
        users_list = [{"_id": str(user["_id"]), "username": user["username"], "role": user["role"]} for user in users]

        return jsonify(users_list), 200
    except PermissionError:
        return jsonify({"message": "Invalid admin credentials"}), 403

# Admin CRUD - Create User
@app.route('/admin/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Admin authentication
    try:
        admin_authenticate(data.get('admin_username'), data.get('admin_password'))
    except PermissionError:
        return jsonify({"message": "Invalid admin credentials"}), 403

    # Check if username and password are provided
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Check if the user already exists
    if users_collection.find_one({"username": username}):
        return jsonify({"message": "Username already taken"}), 400

    # Hash the password
    hashed_password = hash_password(password)

    # Create new user object
    new_user = {
        "username": username,
        "password": hashed_password,
        "role": "user"
    }

    # Insert new user into the database
    result = users_collection.insert_one(new_user)

    # Fetch the newly created user to return their details in the response
    created_user = users_collection.find_one({"_id": result.inserted_id})

    # Remove password from the response data for security reasons
    created_user.pop('password', None)

    # Return a response with the message and created user details, including _id
    return jsonify({
        "message": "User created by admin",
        "user": {
            "id": str(created_user["_id"]),  # Include MongoDB ObjectId as a string
            "username": created_user["username"],
            "role": created_user["role"]
        }
    }), 201

# Admin CRUD - Read User
@app.route('/admin/user/<user_id>', methods=['GET'])
def read_user(user_id):
    try:
        admin_username = request.headers.get('admin_username')
        admin_password = request.headers.get('admin_password')
        # Admin authentication
        admin_authenticate(admin_username, admin_password)

        user = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "username": user["username"],
            "role": user["role"]
        }), 200
    except PermissionError:
        return jsonify({"message": "Invalid admin credentials"}), 403

# Admin CRUD - Update User
@app.route('/admin/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    try:
        admin_authenticate(data.get('admin_username'), data.get('admin_password'))
    except PermissionError:
        return jsonify({"message": "Invalid admin credentials"}), 403

    updated_data = {}
    if 'username' in data:
        updated_data["username"] = data['username']
    if 'password' in data:
        updated_data["password"] = hash_password(data['password'])

    result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})

    if result.matched_count == 0:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"message": "User updated successfully"}), 200

# Admin CRUD - Delete User
@app.route('/admin/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        admin_authenticate(request.args.get('admin_username'), request.args.get('admin_password'))
    except PermissionError:
        return jsonify({"message": "Invalid admin credentials"}), 403

    result = users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200

# Helper function to authenticate admin
def admin_authenticate(username, password):
    admin = users_collection.find_one({"username": username, "role": "admin"})

    if not admin or not check_password(admin["password"], password):
        raise PermissionError("Invalid admin credentials")

if __name__ == '__main__':
    app.run(debug=True)
