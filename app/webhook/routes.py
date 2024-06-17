from flask import Blueprint, request, jsonify, render_template
from app.extensions import mongo
import datetime
import uuid

webhook = Blueprint('webhook', __name__, url_prefix='/webhook')


@webhook.route("/hello", methods=["GET"])
def hello_route():
    return "Hello, world!"


@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    request_id = str(uuid.uuid4())  # Generate a unique request ID

    event = {
        "_id": request_id,
        "request_id": request_id,
        "author": None,
        "action": None,
        "from_branch": None,
        "to_branch": None,
        "timestamp": datetime.datetime.now()
    }

    if event_type == "push":
        event.update({
            "action": "PUSH",
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
        })
    elif event_type == "pull_request":
        event.update({
            "action": "PULL_REQUEST",
            "author": data['pull_request']['user']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
        })
    elif event_type == "merge":
        event.update({
            "action": "MERGE",
            "author": data['sender']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
        })
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


@webhook.route('/events/html', methods=["GET"])
def get_events_html():
    events = list(mongo.db.events.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return render_template('events.html', events=events)
