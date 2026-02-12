# main.py
import webbrowser

BACKEND_URL = "http://localhost:7001"

# Step 1: Open login page in browser
login_url = f"{BACKEND_URL}/login?app=CLI"
print("Open this URL in your browser and log in:")
print(login_url)
# webbrowser.open(login_url)

# Step 2: After login, OAuth redirects to backend and displays the JWT
jwt_token = input("\nAfter login, copy the JWT from the browser and paste it here: ").strip()

# Step 3: Use JWT in your CLI requests
print("\nJWT received! You can now use it to make authenticated requests.")
print(f"Your JWT: {jwt_token}")

# Example: Use JWT in a request to a protected endpoint
import requests
headers = {"Authorization": f"Bearer {jwt_token}"}
response = requests.get(f"{BACKEND_URL}/protected-endpoint", headers=headers)


# Printing
# Convert the response to a dict
data = response.json()  # <-- this step is missing in your code

# Top-level fields
message = data['message']
success = data['success']


# Nested fields inside 'user_info'
user_info = data['user_info']
email = user_info['email']
name = user_info['name']
sub = user_info['sub']
exp = user_info['exp']

# Print to verify
print("Message:", message)
print("Success:", success)
print("Name:", name)
print("Email:", email)
print("Sub:", sub)
print("Expiration (epoch):", exp)