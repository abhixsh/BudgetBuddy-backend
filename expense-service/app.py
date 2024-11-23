from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# MongoDB Atlas connection
mongo_client = MongoClient("mongodb+srv://<username>:<password>@cluster.mongodb.net/user_db")
db = mongo_client['user_db']

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if db.users.find_one({"username": data['username']}):
        return jsonify({"error": "User already exists"}), 400
    db.users.insert_one({
        "username": data['username'],
        "password": generate_password_hash(data['password'])
    })
    return jsonify({"message": "User registered"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({"username": data['username']})
    if user and check_password_hash(user['password'], data['password']):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
