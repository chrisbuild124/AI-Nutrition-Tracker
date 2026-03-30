from flask import Flask, jsonify, redirect, request, url_for, render_template, make_response
import jwt
import requests

# -----------------------------
# A front end flask service to run the calorie counter application.
# Talks directly to the following:
# - Calorie Tracker Backend
# - Auth0 Backend Microservice
# -----------------------------
PORT = 8000
DEBUG_MODE = True

BACKEND_URL = 'http://localhost:8001'
BACKEND_LOGIN_URL = 'http://localhost:7001'
BACKEND_CALORIE_URL = 'http://localhost:7003'
app = Flask(__name__)

# ---------------------
# Routes - Login/Logout/Edit
# ---------------------
@app.route("/")
def frontend_home():
    return render_template("login.html")

@app.route("/login")
def login():
    """
    Redirects to Auth0 Backend Microservice
    """
    return redirect(f"{BACKEND_LOGIN_URL}/login?app-type=Flask")

@app.route("/calorie-counter/dashboard")
def calorie_counter_home():
    """
    Renders homepage
    Talks to calorie tracker backend
    """
    # Verify token
    token = get_token()
    if not token:
        print("Cookie not found")
        return redirect(url_for("frontend_home"))

    # user_info will be in the response if it's successful.
    resp = get_user_info(token)
    if not resp.json().get("success", None):
        print("User verification failed.")
        return redirect(url_for("logout"))
    user_id = resp.json().get("user_id")

    return render_template("calorie-counter/dashboard.html", user_id=user_id)

@app.route("/calorie-counter/edit-profile")
def calorie_counter_edit_profile():
    """
    Renders edit-profile
    Talks to calorie tracker backend
    """
    # Verify token
    token = get_token()
    if not token:
        print("Cookie not found")
        return redirect(url_for("frontend_home"))

    # user_info will be in the response if it's successful.
    resp = get_user_info(token)
    if not resp.json().get("success", None):
        print("User verification failed.")
        return redirect(url_for("logout"))
    user_id = resp.json().get("user_id")

    return render_template("calorie-counter/edit-profile.html", user_id=user_id)

@app.route("/logout")
def logout():
    """
    Logs user out
    """
    # Sends cookie to redis backend (then to redis) to invalidate
    token = request.cookies.get("jwt_calorie_counter_profile")
    if not token:
        print("Cookie not found")
        return redirect(url_for("frontend_home"))
    headers = {"Authorization": token}
    response = requests.get(f"{BACKEND_URL}/logout", headers=headers) # If invalid, will continue anyway

    # Inserts invalid cookie into browser and redirects
    response = make_response(redirect(url_for("frontend_home")))
    response.set_cookie("jwt_calorie_counter_profile", "", expires=0, httponly=True, secure=False)
    return response

# ---------------------
# Routes - Handles API calls
# ---------------------
@app.route("/get_calorie_graph")
def get_calorie_graph():
    user_id = request.args.get('user_id')
    date = request.args.get('date')
    resp = requests.get(f"{BACKEND_URL}/get_calorie_graph", params={'user_id': user_id, 'date': date})
    return jsonify(resp.json()), resp.status_code

@app.route("/get_calories")
def get_calories():
    date = request.args.get('date')
    user_id = request.args.get('user_id')
    resp = requests.get(f"{BACKEND_CALORIE_URL}/get_calories", params={'date': date, 'user_id': user_id})
    return jsonify(resp.json()), resp.status_code

@app.route("/add_calorie", methods=['POST'])
def add_calorie():
    data = request.get_json()
    resp = requests.post(f"{BACKEND_CALORIE_URL}/add_calorie", json=data)
    return jsonify(resp.json()), resp.status_code

@app.route("/delete_calorie/<int:entry_id>", methods=['DELETE'])
def delete_calorie(entry_id):
    resp = requests.delete(f"{BACKEND_CALORIE_URL}/delete_calorie/{entry_id}")
    return jsonify(resp.json()), resp.status_code

@app.route("/openAICalc", methods=['POST'])
def openAICalc():
    """
    Retrieves calorie amount from backend
    Talks to calorie tracker backend
    """
    data = request.get_json()
    resp = requests.post(f"{BACKEND_URL}/openAICalc", json=data)
    return jsonify(resp.json()), resp.status_code

# ---------------------
# Helpers
# ---------------------
def get_token():
    """
    Verifies token works
    """
    return request.cookies.get("jwt_calorie_counter_profile")

def get_user_info(token):
    """
    Retrieves user info
    """
    headers = {"Authorization": token}
    resp = requests.get(f"{BACKEND_URL}/update_JWT_token", headers=headers)
    return resp

if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG_MODE)