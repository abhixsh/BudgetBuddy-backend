from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB using the URI from .env file
client = MongoClient(os.getenv("MONGO_URI"))
db = client.expense_manager  # Database name
expenses_collection = db.expenses  # Collection name

# Route to create a new expense
@app.route('/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.json
        
        # Check if all required fields are provided
        if not all(field in data for field in ["description", "amount", "category", "date"]):
            return jsonify({"error": "Missing required fields"}), 400

        expense = {
            "description": data["description"],
            "amount": data["amount"],
            "category": data["category"],
            "date": data["date"]
        }
        result = expenses_collection.insert_one(expense)
        return jsonify({"message": "Expense added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": f"Error adding expense: {str(e)}"}), 400

# Route to get all expenses
@app.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = list(expenses_collection.find())
        for expense in expenses:
            expense["_id"] = str(expense["_id"])  # Convert ObjectId to string
        return jsonify(expenses), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving expenses: {str(e)}"}), 400

# Route to get a single expense by ID
@app.route('/expenses/<expense_id>', methods=['GET'])
def get_expense(expense_id):
    try:
        # Convert expense_id to ObjectId
        if not ObjectId.is_valid(expense_id):
            return jsonify({"error": "Invalid expense ID format"}), 400

        expense = expenses_collection.find_one({"_id": ObjectId(expense_id)})
        if expense:
            expense["_id"] = str(expense["_id"])  # Convert ObjectId to string
            return jsonify(expense), 200
        else:
            return jsonify({"error": "Expense not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving expense: {str(e)}"}), 400

# Route to update an expense by ID
@app.route('/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    try:
        # Convert expense_id to ObjectId
        if not ObjectId.is_valid(expense_id):
            return jsonify({"error": "Invalid expense ID format"}), 400

        # Check if the request body contains the necessary fields
        updated_expense = {
            "description": request.json.get("description"),
            "amount": request.json.get("amount"),
            "category": request.json.get("category"),
            "date": request.json.get("date")
        }

        # Filter out any None values (fields not provided)
        updated_expense = {key: value for key, value in updated_expense.items() if value is not None}

        if not updated_expense:
            return jsonify({"error": "No fields provided to update"}), 400

        result = expenses_collection.update_one({"_id": ObjectId(expense_id)}, {"$set": updated_expense})
        if result.matched_count > 0:
            return jsonify({"message": "Expense updated"}), 200
        else:
            return jsonify({"error": "Expense not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error updating expense: {str(e)}"}), 400

# Route to delete an expense by ID
@app.route('/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        # Convert expense_id to ObjectId
        if not ObjectId.is_valid(expense_id):
            return jsonify({"error": "Invalid expense ID format"}), 400

        result = expenses_collection.delete_one({"_id": ObjectId(expense_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Expense deleted"}), 200
        else:
            return jsonify({"error": "Expense not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error deleting expense: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5002)
