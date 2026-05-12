import os
import jwt
import datetime
import bcrypt
from functools import wraps
from flask import Flask, request, jsonify
from pydantic import ValidationError
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

from security import token_required, sanitize_string, LoginSchema, RegisterSchema

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Izinkan semua origin untuk development (bisa dibatasi nanti)

# Konfigurasi MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['quick_hire']  # Nama database
users_collection = db['users']  # Nama koleksi

# Secret Key untuk JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# --- Helper Functions ---



# --- Routes ---

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        validated_data = RegisterSchema(**data)
        
        username = validated_data.username
        email = validated_data.email
        password = validated_data.password

        # Cek apakah user sudah ada
        if users_collection.find_one({'email': email}):
            return jsonify({'message': 'User already exists!'}), 409

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Simpan ke MongoDB
        new_user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow()
        }
        users_collection.insert_one(new_user)

        return jsonify({'message': 'User registered successfully!'}), 201
    except ValidationError as e:
        # Jika validasi gagal, kirim error detail ke frontend
        errors = [error['msg'] for error in e.errors()]
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400
    
    except Exception as e:
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        validated_data = LoginSchema(**data)
            
        email = validated_data.email
        password = validated_data.password

        # Cari user di database
        user = users_collection.find_one({'email': email})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Buat Token JWT
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm="HS256")

            return jsonify({
                'message': 'Login successful!',
                'token': token,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid email or password!'}), 401
    except ValidationError as e:
        errors = [error['msg'] for error in e.errors()]
        return jsonify({'message': 'Validation failed', 'errors': errors}), 400

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user_id):
    return jsonify({
        'message': f'Hello, this is a protected route. User ID: {current_user_id}'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)