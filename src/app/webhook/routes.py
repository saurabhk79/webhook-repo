from flask import Blueprint, request, jsonify
from app.extensions import mongo
import datetime

webhook = Blueprint('webhook', __name__, url_prefix='/webhook')


@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == "push":
        event = {
            "event": "PUSH",
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
            "timestamp": datetime.datetime.now()
        }
    elif event_type == "pull_request":
        event = {
            "event": "PULL_REQUEST",
            "author": data['pull_request']['user']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
            "timestamp": datetime.datetime.now()
        }
    elif event_type == "merge":
        event = {
            "event": "MERGE",
            "author": data['sender']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
            "timestamp": datetime.datetime.now()
        }
    else:
        return "Event not supported", 400

    mongo.db.events.insert_one(event)
    return jsonify({"message": "Success"}), 200


@webhook.route('/events', methods=["GET"])
def get_events():
    events = list(mongo.db.events.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)
