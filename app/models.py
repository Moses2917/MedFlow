from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin):
    def __init__(self, email, password, role):
        self.email = email
        self.password = password
        self.role = role
        self.authenticated = True
        self.active = True

    def check_password(self, password):
        return self.password == password

    def to_dict(self):
        return {
            'email': self.email,
            'password_hash': self.password,
            'role': self.role
        }
    
    @property 
    def is_active(self):
        self.acitve = True
        return self.active

    @property
    def is_authenticated(self):
        self.authenticated = True
        return self.authenticated
    
    def get_id(self):
        return "user"

def load_user(user_id):
    user_data = db.users.find_one({'_id': user_id})
    if user_data:
        return User(user_data['email'], user_data['password_hash'], user_data['role'])
    return None