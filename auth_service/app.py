from flask import Flask, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# OAuth setup
oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
)

# Routes
@app.route("/")
def home():
    return "Auth Service Running"

@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=os.getenv("AUTH0_CALLBACK_URL")
    )

@app.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    user = token["userinfo"]
    session["user"] = {
        "email": user["email"],
        "name": user.get("name")
    }
    return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    return jsonify(session["user"])

@app.route("/auth/status")
def auth_status():
    if "user" in session:
        return jsonify({"authenticated": True, "user": session["user"]})
    return jsonify({"authenticated": False})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
