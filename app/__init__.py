from flask import Flask
from .webhook.routes import webhook
from .extensions import mongo


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb+srv://saurabh-from-techstax:techstax@cluster0.zzf0lgm.mongodb.net/webhooks?retryWrites=true&w=majority&appName=Cluster0"

    mongo.init_app(app)
    app.register_blueprint(webhook)

    return app
