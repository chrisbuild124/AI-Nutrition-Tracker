from flask import Flask, redirect, request, url_for, render_template, make_response
import jwt
import requests

# -----------------------------
# A front end flask service to run the calorie counter application.
# Retrieves JWT cookie from backend. 
# -----------------------------
PORT = 5000
DEBUG_MODE = True

BACKEND_URL = 'http://localhost:7001/'
app = Flask(__name__)

# ---------------------
# Routes
# ---------------------
@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/login")
def login():
    # Http 302 code response and URL
    return redirect(f"{BACKEND_URL}/login?app-type=Flask")
    
@app.route("/calorie-counter/home")
def calorie_counter_home():
    """
    Validates JWT token and then moves user to homepage
    """
    token = request.cookies.get("jwt_calorie_counter_profile")

    if not token:
        print("Cookie not found")
        return redirect(url_for("login"))

    # user_info will be in the response if it's successful.
    headers = {"Authorization": token}
    resp = requests.get(f"{BACKEND_URL}/verify-user", headers=headers)
    if not resp.json().get("success", None):
        print("User verification failed.")
        return redirect(url_for("logout"))
    user_info = resp.json().get("user_info")

    return render_template("calorie-counter/home.html", user=user_info)

@app.route("/logout")
def logout():
    """
    Invalidates the JWT cookie
    """
    response = make_response(redirect(url_for("welcome")))
    response.set_cookie("jwt_calorie_counter_profile", "", expires=0, httponly=True, secure=False)
    return response

if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG_MODE)