# Imports
from flask import Flask, request          # Web framework for Cloud Run
import os                                 # For reading environment variables
import json                               # For formatting data as JSON
from google.cloud import pubsub_v1        # Pub/Sub publisher client

# Initialize Flask app
app = Flask(__name__)

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()

# Get environment variables
GCP_PROJECT = os.getenv("GCP_PROJECT")
TOPIC_NAME = os.getenv("TOPIC_NAME")

# Validate environment variables
if not GCP_PROJECT or not TOPIC_NAME:
    raise Exception("Missing required environment variables: GCP_PROJECT or TOPIC_NAME")

# Get full topic path
topic_path = publisher.topic_path(GCP_PROJECT, TOPIC_NAME)

# Cloud Run will POST here when a file is uploaded to the bucket
@app.route("/", methods=["POST"])
def index():
    print("✅ POST request received by Cloud Run")  # Debug print

    try:
        envelope = request.get_json()

        if not envelope:
            print("⚠️ No JSON payload received")
            return "Bad Request: No JSON", 400

        # Extract file metadata
        name = envelope.get('name', 'unknown')
        size = envelope.get('size', '0')
        content_type = envelope.get('contentType', 'unknown')

        # Build message to publish
        message = {
            "filename": name,
            "size": str(size),
            "format": content_type
        }

        # Publish to Pub/Sub
        publisher.publish(topic_path, json.dumps(message).encode("utf-8"))

        # Log the message for screenshot proof
        print(f"📦 Published message: {message}")

        return "OK", 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Internal Server Error: {e}", 500
