from flask import Flask, redirect, request, url_for, render_template, make_response
import jwt
from dotenv import load_dotenv
import requests
import os

# -----------------------------
# A front end flask service to run the calorie counter application.
# Retrieves cookie from backend
# -----------------------------

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY")
JWT_SHARED_SECRET = os.getenv("JWT_SHARED_SECRET")
BACKEND_URL = os.getenv("BACKEND_URL")

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def welcome():
    return render_template("index.html")

@app.route("/login")
def login():
    # Redirect the user to backend login page for Auth0, identifying as Flask app
    return redirect(f"{BACKEND_URL}/login?app=Flask")
    
@app.route("/calorie-counter/home")
def calorie_counter_home():
    print("Secret loaded:", JWT_SHARED_SECRET)
    token = request.cookies.get("jwt")
    if not token:
        print("Cookie not found")
        return redirect(url_for("login"))

    try:
        user_info = jwt.decode(token, JWT_SHARED_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("JWT expired")
        return redirect(url_for("login"))
    except jwt.InvalidTokenError:
        print("Invalid JWT")

        decoded_unverified = jwt.decode(
            token,
            options={"verify_signature": False}
        )

        print("UNVERIFIED PAYLOAD:", decoded_unverified)

        return redirect(url_for("login"))
    



    return render_template("calorie-counter/home.html", user=user_info)

@app.route("/logout")
def logout():
    response = make_response(render_template("logout.html"))
    response.set_cookie("jwt", "", expires=0, httponly=True, secure=False)  # set secure=True in production
    return response

# -----------------------------
# Run locally
# -----------------------------
if __name__ == "__main__":
    app.run(port=8000, debug=True)
