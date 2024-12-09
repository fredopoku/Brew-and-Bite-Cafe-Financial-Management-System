import hashlib
import secrets
import string
from datetime import datetime, timedelta
import jwt

SECRET_KEY = secrets.token_hex(32)  # Generate a secure secret key

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    salted_password = password + salt
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hash_value = hashed_password.split('$')
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest() == hash_value
    except ValueError:
        return False

def generate_reset_token(user_id: int) -> str:
    """Generate a password reset token"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': expiration,
            'purpose': 'password_reset'
        },
        SECRET_KEY,
        algorithm='HS256'
    )

def verify_reset_token(token: str) -> int:
    """Verify a password reset token and return the user ID"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload['purpose'] != 'password_reset':
            return None
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_temporary_password() -> str:
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(12))