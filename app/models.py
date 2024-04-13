from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin):
    def __init__(self, email, password, role):
        self.email = email
        self.password = password
        self.role = role

    def check_password(self, password):
        if(self.password == password):
            result = True
        else:
            result = False
        return result

    def to_dict(self):
        return {
            'email': self.email,
            'password_hash': self.password,
            'role': self.role
        }

def load_user(user_id):
    user_data = db.users.find_one({'_id': user_id})
    if user_data:
        return User(user_data['email'], user_data['password_hash'], user_data['role'], is_hashed=True)
    return None