from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from bson import ObjectId
import jwt
import datetime

app = Flask(__name__)

# Enable CORS with credentials support
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)  # Allow requests from the frontend port (React app)

# MongoDB connection string
mongo_client = MongoClient("mongodb+srv://alokaabishek9:jrTKPYC3wc0eApYt@nutricare.lmquo7d.mongodb.net/?retryWrites=true&w=majority&appName=NutriCare")
db = mongo_client['user_db']

# Secret key for JWT encoding/decoding
SECRET_KEY = 'your_secret_key'

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

# --- Expense Routes ---
# Add Expense (POST /expenses)
@app.route('/expenses', methods=['POST'])
def add_expense():
    try:
        # Get the token from the request headers
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        # Verify the token and get the user ID
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get expense data from the request
        data = request.json
        if not data.get('title') or not data.get('amount'):
            return jsonify({"error": "Title and amount are required"}), 400

        # Insert the expense with the associated user_id
        db.expenses.insert_one({
            "title": data['title'],
            "amount": data['amount'],
            "user_id": ObjectId(user_id)
        })
        return jsonify({"message": "Expense added successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while adding the expense"}), 500

# Get Expenses for a specific user (GET /expenses)
@app.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        # Get the token from the request headers
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        # Verify the token and get the user ID
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Fetch expenses for the logged-in user
        expenses = list(db.expenses.find({"user_id": ObjectId(user_id)}))
        expenses = [{key: object_id_to_str(value) for key, value in expense.items()} for expense in expenses]
        return jsonify(expenses), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching expenses"}), 500

@app.route('/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    try:
        # Get the token from the request headers
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        # Verify the token and get the user ID
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get the new data from the request
        data = request.json
        if not data.get('title') or not data.get('amount'):
            return jsonify({"error": "Title and amount are required"}), 400

        # Find the expense by ID and check if the user owns it
        expense = db.expenses.find_one({"_id": ObjectId(expense_id), "user_id": ObjectId(user_id)})
        if not expense:
            return jsonify({"error": "Expense not found or not authorized to update"}), 404

        # Update the expense
        db.expenses.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": {"title": data['title'], "amount": data['amount']}}
        )
        return jsonify({"message": "Expense updated successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while updating the expense"}), 500


# Delete Expense (DELETE /expenses/<expenseId>)
@app.route('/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        # Get the token from the request headers
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        # Verify the token and get the user ID
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Find the expense by ID and check if the user owns it
        expense = db.expenses.find_one({"_id": ObjectId(expense_id), "user_id": ObjectId(user_id)})
        if not expense:
            return jsonify({"error": "Expense not found or not authorized to delete"}), 404

        # Delete the expense
        db.expenses.delete_one({"_id": ObjectId(expense_id)})
        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while deleting the expense"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
