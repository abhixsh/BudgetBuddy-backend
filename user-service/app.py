from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Atlas connection
mongo_client = MongoClient("mongodb+srv://<username>:<password>@cluster.mongodb.net/expense_db")
db = mongo_client['expense_db']

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    db.expenses.insert_one(data)
    return jsonify({"message": "Expense added"}), 201

@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = list(db.expenses.find())
    return jsonify(expenses), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
