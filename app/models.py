from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin):
    def __init__(self, email, password, role):
        self.email = email
        self.password = password
        self.role = role

    def check_password(self, password):
        return self.password == password

    def to_dict(self):
        return {
            'email': self.email,
            'password_hash': self.password,
            'role': self.role
        }
    
    
    def get_id(self):
        user_id = db.users.find_one({'email': self.email})
        if user_id:
            return str(user_id['_id'])
        return None

    @staticmethod
    def get_by_email(email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(user_data['email'], user_data['password'], user_data['role'])
        return None

# Load user callback
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_email(user_id)