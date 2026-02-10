# backend_auth.py
# ---------------------------------------------------------------------------
# Backend authentication service for Amazon Cognito (PKCE + JWT validation)
# ---------------------------------------------------------------------------

from flask import Flask, request, jsonify, redirect, make_response
from dotenv import load_dotenv
import os
import jwt
import requests
import base64
import hashlib
import secrets

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------
app = Flask(__name__)
load_dotenv()

COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # must point to this backend /finish-login
JWKS_URL = os.getenv("JWKS_URL")
USER_POOL_ID = os.getenv("USER_POOL_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION")
FRONTEND_CALLBACK_URL = os.getenv("FRONTEND_CALLBACK_URL")  # e.g. http://localhost:8000/finish-login

SCOPE = os.getenv("COGNITO_SCOPE", "openid+email+profile")

jwks = requests.get(JWKS_URL).json()

# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------
def generate_pkce_pair():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge

def get_signing_key(kid):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    return None

# ---------------------------------------------------------------------------
# Start login: redirect browser to Cognito
# ---------------------------------------------------------------------------
@app.route("/start-login")
def start_login():
    print('test')
    verifier, challenge = generate_pkce_pair()

    auth_url = (
        f"{COGNITO_DOMAIN}/oauth2/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"code_challenge={challenge}&"
        f"code_challenge_method=S256&"
        f"scope={SCOPE}"
    )
    print(auth_url)
    resp = make_response(redirect(auth_url))
    resp.set_cookie(
        "pkce_verifier",
        verifier,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="Lax",
    )
    return resp

# ---------------------------------------------------------------------------
# Finish login: Cognito callback → token exchange → redirect to frontend
# ---------------------------------------------------------------------------
@app.route("/finish-login")
def finish_login():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    verifier = request.cookies.get("pkce_verifier")
    if not verifier:
        return jsonify({"error": "Missing PKCE verifier cookie"}), 400

    token_url = f"{COGNITO_DOMAIN}/oauth2/token"

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_resp = requests.post(token_url, data=data, headers=headers)

    if token_resp.status_code != 200:
        return jsonify({"error": "Token exchange failed", "details": token_resp.text}), 400

    tokens = token_resp.json()

    # Redirect back to frontend with tokens in query (demo-friendly; can be hardened later)
    access_token = tokens.get("access_token", "")
    id_token = tokens.get("id_token", "")

    redirect_url = (
        f"{FRONTEND_CALLBACK_URL}"
        f"?access_token={access_token}"
        f"&id_token={id_token}"
    )

    # Clear PKCE cookie
    resp = make_response(redirect(redirect_url))
    resp.set_cookie("pkce_verifier", "", expires=0)
    return resp

# ---------------------------------------------------------------------------
# Auth check: validate JWT from frontend
# ---------------------------------------------------------------------------
@app.route("/auth-check")
def auth_check():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"authenticated": False, "error": "Missing Authorization header"}), 401

    token = auth_header.replace("Bearer ", "")

    try:
        unverified_header = jwt.get_unverified_header(token)
        signing_key = get_signing_key(unverified_header["kid"])

        if not signing_key:
            return jsonify({"authenticated": False, "error": "Invalid signing key"}), 401

        decoded = jwt.decode(
            token,
            key=jwt.algorithms.RSAAlgorithm.from_jwk(signing_key),
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}",
        )

        return jsonify({"authenticated": True, "claims": decoded})

    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)}), 401

# ---------------------------------------------------------------------------
# Run backend
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    #app.run(port=5000, debug=True)
    with app.test_client() as client: 
        resp = client.get("/start-login") 
        print("STATUS:", resp.status_code) 
        print("JSON:", resp.get_json())
