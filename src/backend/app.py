from flask import Flask, jsonify, redirect, url_for, make_response, request
import requests

# -----------------------------
# A backend flask service to run the calorie counter application.
# Microservices utilized:
# - Calorie Count Microservice: Retrieves amount of calories for in a sentence.
# - Unit conversion Microservice: Unit converter
# - Motivational quote Microservice: Returns a nice quote 
# - Redis routing Microservice: Returns if valid a JWT token
# - MySQL routing Microservice: Returns user information
# -----------------------------

PORT = 8001
DEBUG_MODE = True

BACKEND_LOGIN_URL = 'http://localhost:7001'
BACKEND_REDIS_URL = 'http://localhost:7002'
BACKEND_OPENAI_URL = 'http://localhost:7023'
app = Flask(__name__)

# ---------------------
# Routes - Login/Logout/Edit
# ---------------------
@app.route("/")
def backend_home():
    return "Calorie Calculator Backend Microservice Running"

@app.route("/update_JWT_token")
def update_JWT_token_backend():
    """
    Calls Redis upate_JWT_token to refresh redis database
    """
    token = request.headers.get("Authorization")
    headers = {"Authorization": token}
    redis_resp = requests.get(f"{BACKEND_REDIS_URL}/update_session", headers=headers)
    return make_response(redis_resp.content, redis_resp.status_code, {"Content-Type": "application/json"})

@app.route("/logout")
def logout():
    """
    Invalidates the JWT token in Redis database
    """
    token = request.headers.get("Authorization")
    headers = {"Authorization": token}
    resp = requests.get(f"{BACKEND_REDIS_URL}/delete_session", headers=headers)
    return make_response(resp.content, resp.status_code, {"Content-Type": "application/json"})

# ---------------------
# Routes - Handles API calls
# ---------------------
@app.route("/openAICalc", methods=['POST'])
def openAICalc():
    """
    Retrieves calorie amount from openAI microservice
    Talks to calorie tracker backend
    """
    data = request.get_json()
    resp = requests.post(f"{BACKEND_OPENAI_URL}/count-calories", json=data)
    data = resp.json()
    return jsonify(data), resp.status_code

if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG_MODE)