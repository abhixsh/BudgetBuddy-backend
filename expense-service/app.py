from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

mongo_client = MongoClient("mongodb+srv://alokaabishek9:jrTKPYC3wc0eApYt@nutricare.lmquo7d.mongodb.net/?retryWrites=true&w=majority&appName=NutriCare")
db = mongo_client['user_db']

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
