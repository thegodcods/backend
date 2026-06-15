import os
import jwt
import datetime
import bcrypt
from bson import ObjectId
from functools import wraps
from flask import Flask, request, jsonify
from pydantic import ValidationError
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from security import token_required, sanitize_string, LoginSchema, RegisterSchema
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
@token_required
def analyze_pdf(current_user_id):
    try:
        files = request.files.getlist("image")
        job_deskription = request.form.get("job_description")
        arr_result = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            results = [executor.submit(processing_file, file, job_deskription) for file in files]
            for result in results:
                score, job_struct, cv_struct, filename = result.result()
                print(f"score: {score}, job_struct: {job_struct}, cv_struct: {cv_struct}, filename: {filename}")
                arr_result.append({
                    "score": score,
                    "cv_struct": cv_struct,
                    "name": filename.split(".")[0]
                })
        # simpan ke database screenings
        screenings_record = {
            "user_id": current_user_id,
            "job_deskription": job_deskription,
            "created_at": datetime.datetime.utcnow(),
            "result": arr_result
        }
        screenings_collection = db['screenings']
        screenings_collection.insert_one(screenings_record)
        return jsonify({"status": 200, "message": "Success", "data": {"job_deskription": job_deskription, "result": arr_result}}), 200
    except Exception as e:
        return jsonify({"status": 500, "message": "Failed Upload"}), 500
    
@app.route("/api/screenings", methods=["GET"])
@token_required
def get_screenings(current_user_id):
    screenings_collection = db['screenings']
    # urutkan berdaarkan created_at
    screenings = screenings_collection.find({"user_id": current_user_id}).sort("created_at", -1)
    history = []

    for s in screenings:
        history.append({
            "job_deskription": s["job_deskription"],
            "result": s["result"],
            "created_at": s["created_at"]
        })
    return jsonify({"status": 200, "message": "Success", "data": history}), 200

# buat api perankingan berdasarkan score
@app.route("/api/ranking", methods=["GET"])
@token_required
def get_ranking(current_user_id):
    scrennings = db['screenings']
    screenings_result = scrennings.find({"user_id": current_user_id}).sort("created_at", -1)
    cv_result = screenings_result.get("result")

@app.route("/api/ranking/<screening_id>", methods=["GET"])
@token_required
def get_ranking_by_id(current_user_id, screening_id):
    try:
        screenings_collection = db['screenings']
        
        try:
            obj_id = ObjectId(screening_id)
        except Exception:
            return jsonify({
                "status": 400, 
                "message": "Invalid Screening ID format."
            }), 400

        screening_doc = screenings_collection.find_one({
            "_id": obj_id,
            "user_id": current_user_id
        })

        if not screening_doc:
            return jsonify({
                "status": 404, 
                "message": "Screening not found or access denied."
            }), 404

        results = screening_doc.get("result", [])
        
        if not results:
            return jsonify({
                "status": 200, 
                "message": "Screening found but no candidates processed.", 
                "data": []
            }), 200

        ranked_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        final_data = []
        for rank, item in enumerate(ranked_results, start=1):
            final_data.append({
                "rank": rank,
                "name": item.get("name"),
                "score": round(item.get("score", 0), 4), 
                "cv_struct": item.get("cv_struct", ""),
            })

        return jsonify({
            "status": 200,
            "message": "Success",
            "data": {
                "screening_id": str(screening_doc['_id']),
                "job_description_preview": screening_doc.get('job_deskription', '')[:100] + "...",
                "total_candidates": len(final_data),
                "created_at": screening_doc.get('created_at'),
                "ranked_list": final_data
            }
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": 500, 
            "message": f"Internal Server Error: {str(e)}"
        }), 500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)