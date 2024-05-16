from flask import Flask
from pymongo import MongoClient
from flask_login import LoginManager
import config
from os import getcwd

app = Flask(__name__)
app.config.from_object(config)
app.config['UPLOAD_FOLDER'] = getcwd()+"\\app\\static\\pdf\\"

# Connect to MongoDB
mongo = MongoClient(app.config['MONGO_URI'])
db = mongo.get_database("MedicalData")#app.config['MONGO_DB_NAME'])

login_manager = LoginManager(app)
from app import routes, models
from app.models import load_user
login_manager.user_loader(load_user)