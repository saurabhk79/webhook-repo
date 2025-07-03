import os
from flask import Flask, render_template
from app.webhook.routes import webhook
from .extensions import mongo

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, "../templates")
    static_dir = os.path.join(base_dir, "../static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)    

    app.config["MONGO_URI"] = "mongodb://localhost:27017/webhook_db"
    mongo.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app

