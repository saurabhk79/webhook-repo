from flask import Flask
from .webhook.routes import webhook
from .extensions import mongo

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/webhook"

    mongo.init_app(app)

    app.register_blueprint(webhook)

    return app
