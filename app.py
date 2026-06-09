import os
import jwt
import datetime
import bcrypt
import asyncio
from functools import wraps
from flask import Flask, request, jsonify
from pydantic import ValidationError
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

from security import token_required, sanitize_string, LoginSchema, RegisterSchema
from ekstraksi_pdf import ekstraksi_pdf_cv
from clean_text import cleaning
from text_processor import clean_cv_text, get_embedding, inspect_tokens
from processing import processing_file
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

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        validated_data = RegisterSchema(**data)
        
        username = validated_data.username
        email = validated_data.email
        password = validated_data.password

        # Cek apakah user sudah ada
        if users_collection.find_one({'email': email}):
            return jsonify({
                "status": 409,
                'message': 'User already exists!'}), 409

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

        return jsonify({
            'status': 201,
            'message': 'User registered successfully!'}), 201
    except ValidationError as e:
        # Jika validasi gagal, kirim error detail ke frontend
        errors = [error['msg'] for error in e.errors()]
        return jsonify({"status": 400, 'message': 'Validation failed', 'errors': errors}), 400
    
    except Exception as e:
        return jsonify({"status": 500, 'message': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
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
                'status': 200,
                'message': 'Login successful!',
                'data': {
                    'token': token,
                    'user': {
                        'id': str(user['_id']),
                        'username': user['username'],
                        'email': user['email']
                    }
                }
            }), 200
        else:
            return jsonify({'status': 401, 'message': 'Invalid email or password!'}), 401
    except ValidationError as e:
        errors = [error['msg'] for error in e.errors()]
        return jsonify({'status': 400, 'message': 'Validation failed', 'errors': errors}), 400

@app.route('/api/protected', methods=['GET'])
@token_required
def protected_route(current_user_id):
    return jsonify({
        'status': 200,
        'message': f'Hello, this is a protected route. User ID: {current_user_id}'
    }), 200

@app.route("/api/analyze", methods=["POST"])
def analyze_pdf():
    files = request.files.getlist("image")
    arr_result = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = [executor.submit(processing_file, file) for file in files]
        for result in results:
            token, vec_cv, clean_cv, filename = result.result()
            arr_result.append({
                "token": token,
                "vektor": vec_cv.tolist(),
                "text": clean_cv,
                "filename": filename
            })

    # for file in files:
    #     text = ekstraksi_pdf_cv(file, file.filename)
    #     clean_cv = clean_cv_text(text)
    #     vec_cv = get_embedding(clean_cv)
    #     token = inspect_tokens(clean_cv)
    #     arr_token.append(token)
    #     arr_vector.append(vec_cv.tolist())
    #     arr_text.append(clean_cv)

    return jsonify({"status": 200, "message": "Success", "data": arr_result}), 200
    # if file:
    #     text = ekstraksi_pdf_cv(file, file.filename)
    #     clean_cv = clean_cv_text(text)
    #     vec_cv = get_embedding(clean_cv)
    #     token = inspect_tokens(clean_cv)
    #     return jsonify({"token": token, "vektor": vec_cv.tolist(), "text": clean_cv}), 200
    # else:
    #     return jsonify({"error": "No file uploaded"}), 400
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)