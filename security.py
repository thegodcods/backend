from functools import wraps
from flask import request, jsonify
import jwt
from pydantic import BaseModel, EmailStr, field_validator
import re, os
import bleach
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Ambil token dari header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user_id, *args, **kwargs)
    return decorated

# --- Helper untuk Sanitasi String (Mencegah XSS/NoSQL Injection) ---
def sanitize_string(value: str) -> str:
    if not value:
        return value
    # Bleach akan menghapus tag HTML berbahaya seperti <script>
    cleaned = bleach.clean(value, tags=[], attributes={}, strip=True)
    # Hapus karakter null byte yang bisa mengganggu MongoDB
    cleaned = cleaned.replace('\x00', '')
    return cleaned.strip()

# --- Skema Validasi Register ---
class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str

    # Validasi Username
    @field_validator('username')
    def validate_username(cls, v):
        v = sanitize_string(v)
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Username harus antara 3-20 karakter')
        # Hanya izinkan huruf, angka, underscore, dan titik
        if not re.match(r'^[a-zA-Z0-9_.]+$', v):
            raise ValueError('Username hanya boleh berisi huruf, angka, underscore, dan titik')
        return v

    # Validasi Email
    @field_validator('email')
    def validate_email(cls, v):
        v = sanitize_string(v).lower()
        # Regex sederhana untuk email (Pydantic EmailStr lebih baik jika install email-validator)
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Format email tidak valid')
        return v

    # Validasi Password
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password harus mengandung setidaknya satu huruf besar')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password harus mengandung setidaknya satu huruf kecil')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password harus mengandung setidaknya satu angka')
        return v

# --- Skema Validasi Login ---
class LoginSchema(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def validate_email(cls, v):
        return sanitize_string(v).lower()
    
    @field_validator('password')
    def validate_password(cls, v):
        return sanitize_string(v)