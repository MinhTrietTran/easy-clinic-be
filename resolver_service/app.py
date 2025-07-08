from flask import Flask, request, jsonify

app = Flask(__name__)

# Hardcoded mapping for local development
SERVICE_PUBLIC_MAP = {
    "user_service": {"address": "localhost", "port": 5001},
    # Add more services here as needed
    "appointment_service": {"address": "localhost", "port": 5002},
    # "medical_record_service": {"address": "localhost", "port": 5003},
    # "analytics_service": {"address": "localhost", "port": 5004},
}

@app.route("/resolve")
def resolve():
    service = request.args.get("service")
    if not service:
        return jsonify({"error": "Missing service"}), 400

    info = SERVICE_PUBLIC_MAP.get(service)
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "Service not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
