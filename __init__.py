from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')

mongo = None
login_manager = None

def initialize_extensions(app):
    global mongo, login_manager
    mongo = PyMongo(app)
    login_manager = LoginManager(app)
    from app.models import load_user
    login_manager.user_loader(load_user)

from app import routes, models
initialize_extensions(app)