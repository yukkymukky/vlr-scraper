from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import json

app = Flask(__name__)
CORS(app) 

@app.route("/wrapped", methods=["GET"])
def get_wrapped():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    json_path = f"wrapped-data/{username}_wrapped.json"
    print(f"Looking for file at: {json_path}")

    # If the wrapped file already exists, just return it
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)

    # Otherwise, run Scrapy to generate it
    try:
        subprocess.run(
            ["scrapy", "crawl", "vlr", "-a", f"username={username}"],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Scrapy failed", "details": e.stderr.decode()}), 500

    if not os.path.exists(json_path):
        return jsonify({"error": "Wrapped file not found"}), 404

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data)

@app.route("/")
def serve_frontend():
    return app.send_static_file("wrapped.html")

if __name__ == "__main__":
    app.run(debug=True)
