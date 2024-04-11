import secrets
from os import environ as ENV
SECRET_KEY = secrets.token_urlsafe(32)
MONGO_URI = "mongodb+srv://{}@cluster0.qhwjzyt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(ENV.get('mongo_user')+":"+ENV.get('mongo_pass'))