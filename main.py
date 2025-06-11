# Imports
from flask import Flask, request          # Flask app and request handling
import os                                 # For environment variables
from google.cloud import pubsub_v1        # Pub/Sub client
import json                               # For JSON formatting

# Initialize Flask app
app = Flask(__name__)

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()

# Get topic path using env vars
topic_path = publisher.topic_path(os.getenv("GCP_PROJECT"), os.getenv("TOPIC_NAME"))

# Handle POST requests from Cloud Storage trigger
@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()         # Get JSON payload

    if not envelope:                      # Check if payload exists
        return "Bad Request", 400

    # Extract file metadata
    name = envelope['name']
    size = envelope['size']
    content_type = envelope['contentType']

    # Create message
    message = {
        "filename": name,
        "size": size,
        "format": content_type
    }

    # Publish to Pub/Sub
    publisher.publish(topic_path, json.dumps(message).encode("utf-8"))

    # Log message
    print(f"Published message: {message}")

    return "OK", 200                       # OK response is send
