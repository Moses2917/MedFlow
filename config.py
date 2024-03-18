import secrets
SECRET_KEY = secrets.token_urlsafe(32)
MONGO_URI = "mongodb+srv://{}@cluster0.qhwjzyt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format("INSERT_USER:PASS")
