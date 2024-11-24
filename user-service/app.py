from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)

# MongoDB connection
mongo_client = MongoClient("your_mongodb_connection_string")
db = mongo_client['user_db']

# Secret key for JWT
SECRET_KEY = 'your_secret_key'

# JWT Functions
def generate_token(user_id):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {'user_id': str(user_id), 'exp': expiration_time}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not all(key in data for key in ['username', 'password', 'sex', 'occupation']):
        return jsonify({"error": "All fields are required"}), 400

    if db.users.find_one({"username": data['username']}):
        return jsonify({"error": "User already exists"}), 400

    db.users.insert_one({
        "username": data['username'],
        "password": generate_password_hash(data['password']),
        "sex": data['sex'],
        "occupation": data['occupation']
    })
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({"username": data['username']})
    if user and check_password_hash(user['password'], data['password']):
        token = generate_token(user['_id'])
        return jsonify({"message": "Login successful", "token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
