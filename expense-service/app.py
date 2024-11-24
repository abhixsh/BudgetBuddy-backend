from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection string from environment variable
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['user_db']

# Secret key for JWT from environment variable
SECRET_KEY = os.getenv("SECRET_KEY")

# --- Expense CRUD Operations --- 

# Add an expense
@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    if not all(key in data for key in ['title', 'amount']):
        return jsonify({"error": "Title and amount are required"}), 400

    db.expenses.insert_one({
        "title": data['title'],
        "amount": data['amount']
    })
    return jsonify({"message": "Expense added successfully"}), 201

# Get all expenses
@app.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = list(db.expenses.find())
        
        # Convert ObjectId to string for every expense in the list
        for expense in expenses:
            expense['_id'] = str(expense['_id'])  # Convert ObjectId to string
        
        return jsonify(expenses), 200
    except Exception as e:
        print(f"Error fetching expenses: {e}")
        return jsonify({"error": "Failed to fetch expenses", "message": str(e)}), 500

# Update an expense by ID
@app.route('/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.json
    if not data.get('title') or not data.get('amount'):
        return jsonify({"error": "Title and amount are required"}), 400

    updated_expense = db.expenses.find_one_and_update(
        {"_id": ObjectId(expense_id)},
        {"$set": {"title": data['title'], "amount": data['amount']}},
        return_document=True
    )

    if updated_expense:
        updated_expense['_id'] = str(updated_expense['_id'])  # Convert ObjectId to string
        return jsonify(updated_expense), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

# Delete an expense by ID
@app.route('/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    result = db.expenses.delete_one({"_id": ObjectId(expense_id)})

    if result.deleted_count == 1:
        return jsonify({"message": "Expense deleted successfully"}), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

# Generic error handler to capture unexpected errors
@app.errorhandler(Exception)
def handle_exception(error):
    # Log the full traceback to the console for debugging
    print(f"Error: {error}")
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
