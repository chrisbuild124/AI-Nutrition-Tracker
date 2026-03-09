from flask import Flask, redirect, request, url_for, render_template, make_response
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
app = Flask(__name__)

# ---------------------
# Routes
# ---------------------
@app.route("/")
def frontend_home():
    return render_template("index.html")

@app.route("/login")
def login():
    """
    Redirects to Auth0 Backend Microservice
    """
    return redirect(f"{BACKEND_LOGIN_URL}/login?app-type=Flask")

@app.route("/calorie-counter/home")
def calorie_counter_home():
    """
    Renders homepage
    Talks to calorie tracker backend
    """
    token = request.cookies.get("jwt_calorie_counter_profile")
    if not token:
        print("Cookie not found")
        return redirect(url_for("frontend_home"))

    # user_info will be in the response if it's successful.
    headers = {"Authorization": token}
    resp = requests.get(f"{BACKEND_URL}/update_JWT_token", headers=headers)
    if not resp.json().get("success", None):
        print("User verification failed.")
        return redirect(url_for("logout"))
    user_info = resp.json().get("user_info")

    return render_template("calorie-counter/home.html", user=user_info)

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

# Initialize application
if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG_MODE)