from flask import Blueprint, json, request, jsonify
# from flask import request, jsonify
from datetime import datetime
from bson.json_util import dumps
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    print(f"Received event: {event_type}")
    print(f"Payload: {data}")

    event = None
    timestamp = datetime.now().strftime('%d %B %Y - %I:%M %p UTC')

    if event_type == "push":
        event = {
            "type": "push",
            "author": data["pusher"]["name"],
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": timestamp,
        }

    elif event_type == "pull_request":
        pr = data["pull_request"]
        author = pr["user"]["login"]
        from_branch = pr["head"]["ref"]
        to_branch = pr["base"]["ref"]

        if pr.get("merged", False):
            event = {
                "type": "merge",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp,
            }
        else:
            event = {
                "type": "pull_request",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp,
            }

    else:
        return jsonify({"status": "ignored"}), 200

    mongo.db.events.insert_one(event)
    return jsonify({"status": "saved"}), 200


@webhook.route("/events", methods=["GET"])
def get_events():
    events = mongo.db.events.find().sort("_id", -1).limit(10)
    return dumps(events), 200, {'Content-Type': 'application/json'}
