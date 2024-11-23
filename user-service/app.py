from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from bson import ObjectId

app = Flask(__name__)

# Enable CORS with credentials support
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)  # Allow requests from the frontend port (React app)

# MongoDB connection string
mongo_client = MongoClient("mongodb+srv://alokaabishek9:jrTKPYC3wc0eApYt@nutricare.lmquo7d.mongodb.net/?retryWrites=true&w=majority&appName=NutriCare")
db = mongo_client['user_db']

# Function to convert MongoDB ObjectId to string
def object_id_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# --- Regular User Registration and Login ---
# User Registration (POST /register)
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

# User Login (POST /login)
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

        return jsonify({"message": "Login successful"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the login"}), 500

# --- Admin Routes ---
# Admin Registration (POST /admin/register)
@app.route('/admin/register', methods=['POST'])
def admin_register():
    try:
        data = request.json
        if not data.get('username') or not data.get('password'):
            return jsonify({"error": "Username and password are required"}), 400

        # Check if the admin already exists
        if db.admins.find_one({"username": data['username']}):
            return jsonify({"error": "Admin already exists"}), 400

        # Insert the new admin
        db.admins.insert_one({
            "username": data['username'],
            "password": generate_password_hash(data['password']),
        })
        return jsonify({"message": "Admin registered successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the admin registration"}), 500

# Admin Login (POST /admin/login)
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        admin = db.admins.find_one({"username": username})
        if not admin:
            return jsonify({"error": "Invalid username or password"}), 400

        if not check_password_hash(admin['password'], password):
            return jsonify({"error": "Invalid username or password"}), 400

        return jsonify({"message": "Admin login successful"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the admin login"}), 500

# Admin: Get All Users (GET /admin/users)
@app.route('/admin/users', methods=['GET'])
def get_users():
    try:
        users = list(db.users.find())
        users = [{key: object_id_to_str(value) for key, value in user.items()} for user in users]
        return jsonify(users), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching users"}), 500

# Admin: Delete User (DELETE /admin/users/<user_id>)
@app.route('/admin/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the user"}), 500

# --- Expense Routes ---
# Add Expense (POST /expenses)
@app.route('/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.json
        if not data.get('title') or not data.get('amount'):
            return jsonify({"error": "Title and amount are required"}), 400

        # Insert the expense
        db.expenses.insert_one(data)
        return jsonify({"message": "Expense added successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while adding the expense"}), 500

# Get Expenses (GET /expenses)
@app.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = list(db.expenses.find())
        expenses = [{key: object_id_to_str(value) for key, value in expense.items()} for expense in expenses]
        return jsonify(expenses), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching expenses"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
