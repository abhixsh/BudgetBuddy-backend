from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB Atlas connection
mongo_client = MongoClient("mongodb+srv://alokaabishek9:jrTKPYC3wc0eApYt@nutricare.lmquo7d.mongodb.net/?retryWrites=true&w=majority&appName=NutriCare")
db = mongo_client['user_db']  # Using user_db; you can change it to another db for expenses if needed.

# Function to convert MongoDB ObjectId to string
def object_id_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# Add Expense (POST /expenses)
@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    if not data.get('title') or not data.get('amount'):
        return jsonify({"error": "Title and amount are required"}), 400
    db.expenses.insert_one(data)
    return jsonify({"message": "Expense added successfully"}), 201

# Get Expenses (GET /expenses)
@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = list(db.expenses.find())
    # Convert ObjectId to string for all expense items
    expenses = [{key: object_id_to_str(value) for key, value in expense.items()} for expense in expenses]
    return jsonify(expenses), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
