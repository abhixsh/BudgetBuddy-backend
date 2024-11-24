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
    expenses = list(db.expenses.find())
    for expense in expenses:
        expense['_id'] = str(expense['_id'])
    return jsonify(expenses), 200

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
        updated_expense['_id'] = str(updated_expense['_id'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
