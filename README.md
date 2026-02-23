# Calorie-Tracker Application
- Reach your full physical potential using our calorie tracking application!

### Overview
- 

# NOTES
### Cookies
- Cookie expiration is different than JWT expiration
- Cookie lives in browser and can encapsulate a JWT token
    - JWT token is what is used to authenticate the user

 ### Generating virtual environment
If virtual environment not already generated:
- Find desired location and do `python -m venv <filepath:usually .venv>`
    - `-m` stands for module, and tells python to run library as a script
Activate Virtual Environment:
- `source <path to venv file name>/bin/activate`
    - This runs the virtual environment
If requirements.txt exists and missing modules:
- Do `pip install -r requirements.txt`
Else:
- Install dependencies with `pip install <module?>`
- `pip freeze > requirements.txt` *Note:* ">" redirects output to `requirements.txt`
    - Adds modules to `requirements.txt` to avoid re-installing modules
Deactivate:
- `deactivate` *Note:* Shuts down virtual environment
Download pip modules from requirements.txt:
    - `pip install -r requirements.txt`

### Flask imports
- `Flask`: `Flask(__name__)` - __name__ is the file name - which becomes this module name
- `redirect` - (location:URL, code=302), generates a http response object w/ URL redirect and code 302
- `request` - Retrieves incoming request data
    - `request.args` - URL Parameters (stuff after question mark)
    - `get_json` - returns json data if there is any
- `url_for` - Generate a URL to the given function route name (endpoint)
- `render_template` - (URL, data) Sends html template + data to browser
    - Flask creates the application, render_template relies in jinja2 for dynamic output 
from static files.
- `make_response` - Response object and attach headers.
    - Usually used like: `make_response(render_template(URL, data))` then `return response`

### Flask Routes
`app.route(url)` - adds `func` to internal mapper for url. Decorator (adds functionality to it) but not a wrapper (doesn't create a new function)<br>
`func`

### JWT & PyJwt - Proving Authenticity 
- Import JWT Module:
    - Do NOT: `pip install jwt`
    - Do: `pip install PyJWT`
- JWT = Json Web Token
    - Before encoding
- JWS = Json Web Signature
    - After encoding
- JWT accomplishes:
    - Proves authenticity (permissions if configured too)
        - Since it cannot be tampered    
    - Proves identity (ID inside JWT)
        - Since it cannot be tampered
    - Stateless verification
        - Since it does not need to be verified on the backend server if using seperate redis database 
- Creating JWT:
    - In general, there's two types of JWT: private/public and shared
    - The advantage to using shared is it's a little simpler (among others)
    - To generate the public key and then the private key, do the following in the console:
        - Generate a 2048-bit RSA private key `openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048`
        - Generate the corresponding public key `openssl rsa -pubout -in private.pem -out public.pem`
- `jwt.decode()` - (token, key, algorithm=[""]) *Ex.* - `RS256`
    - `token` - token received
    - `key` - key needed to unlock the algorithm
    - `algorithm` - algorithm needed to decode
        - RS256 = RSA + SHA-256
        - RSA = private/public key pair
        - SHA-256 = hash function
- `jwt.encode()` - (token, key, algorithm=[""]) 
    - Same arguements as above
    - Can insert payload into encode 
