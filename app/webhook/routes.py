from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from bson.json_util import dumps
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@webhook.route("/receiver", methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    print(f"Received event: {event_type}")

    event = {}
    now = datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC')

    if event_type == "push":
        event = {
            "request_id": data["after"],  # Git commit SHA
            "author": data["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": now
        }

    elif event_type == "pull_request":
        pr = data["pull_request"]
        is_merged = pr.get("merged", False)

        event = {
            "request_id": str(pr["id"]),  # PR ID
            "author": pr["user"]["login"],
            "action": "MERGE" if is_merged else "PULL_REQUEST",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": now
        }

    else:
        return jsonify({"status": "ignored"}), 200

    mongo.db.events.insert_one(event)
    return jsonify({"status": "saved"}), 200


@webhook.route("/events", methods=["GET"])
def get_events():
    events = mongo.db.events.find().sort("timestamp", -1).limit(10)

    result = []
    for e in events:
        formatted = {
            "action": e.get("action"),
            "author": e.get("author"),
            "timestamp": e.get("timestamp")
        }

        if e["action"] == "PUSH":
            formatted["to_branch"] = e.get("to_branch")

        else:
            formatted["from_branch"] = e.get("from_branch")
            formatted["to_branch"] = e.get("to_branch")

        result.append(formatted)

    return dumps(result), 200, {'Content-Type': 'application/json'}
