from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import jwt

app = Flask(__name__)

# MongoDB connection
mongo_client = MongoClient("your_mongodb_connection_string")
db = mongo_client['expense_db']

# Secret key for JWT
SECRET_KEY = 'your_secret_key'

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@app.route('/expenses', methods=['POST'])
def add_expense():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    data = request.json
    if not all(key in data for key in ['title', 'amount']):
        return jsonify({"error": "Title and amount are required"}), 400

    db.expenses.insert_one({
        "title": data['title'],
        "amount": data['amount'],
        "user_id": ObjectId(user_id)
    })
    return jsonify({"message": "Expense added successfully"}), 201

@app.route('/expenses', methods=['GET'])
def get_expenses():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    expenses = list(db.expenses.find({"user_id": ObjectId(user_id)}))
    for expense in expenses:
        expense['_id'] = str(expense['_id'])
    return jsonify(expenses), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
