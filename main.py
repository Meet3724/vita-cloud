# Imports
from flask import Flask, request           # Web framework
import os                                  # For env vars
import json                                # To format messages
from google.cloud import pubsub_v1         # Pub/Sub client

# Initialize Flask app
app = Flask(__name__)

# Init Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()

# Get env variables
GCP_PROJECT = os.getenv("GCP_PROJECT")
TOPIC_NAME = os.getenv("TOPIC_NAME")

# Check if env vars are set
if not GCP_PROJECT or not TOPIC_NAME:
    raise Exception("Missing env vars")

# Get full topic path
topic_path = publisher.topic_path(GCP_PROJECT, TOPIC_NAME)

# Handle POST requests
@app.route("/", methods=["POST"])
def index():
    try:
        envelope = request.get_json()  # Read JSON payload
        if not envelope:
            print("No payload")
            return "Bad Request", 400

        # Get file metadata
        name = envelope.get('name', 'unknown')
        size = envelope.get('size', '0')
        content_type = envelope.get('contentType', 'unknown')

        # Create message for Pub/Sub
        message = {
            "filename": name,
            "size": str(size),
            "format": content_type
        }

        # Publish message
        publisher.publish(topic_path, json.dumps(message).encode("utf-8"))
        print(f"Published message: {message}")

        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return f"Internal Server Error: {e}", 500
