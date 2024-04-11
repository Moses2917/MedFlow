from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin):
    def __init__(self, email, password, role, is_hashed=False):
        self.email = email
        self.password_hash = generate_password_hash(password) if not is_hashed else password
        self.role = role

    def check_password(self, password):
        result = check_password_hash(self.password_hash, password)
        return result

    def to_dict(self):
        return {
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role
        }

def load_user(user_id):
    user_data = db.users.find_one({'_id': user_id})
    if user_data:
        return User(user_data['email'], user_data['password_hash'], user_data['role'], is_hashed=True)
    return None