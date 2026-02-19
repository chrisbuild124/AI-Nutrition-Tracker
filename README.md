## Securing Oauth 0 to web dev front end
### Web login
Start:
- Call URL for homepage to login
- Homepage is redirected to /login
- /login redirects to backend login
    - /login just redirects to backend login, it could be removed and added to html, but this keeps things in order. 

Backend Login:
- Finds the system the user is coming from (CLI or Flask)
- Creates a URL and the user is redirected to Auth 2.0's login page for the specific login (CLI or Flask) and asks the user to login into Auth 2.0's authentication (CLI or Flask) database.
    - Each database holds its own login records.
    - User can login using google or create a login (CLI or Flask)
    - User is logged in and sent to the backend's database's /callback URL. 

Backend Callback & why use JWT if the Auth code is a secure request:
- After Auth 2.0 is completed, backend server receives auth code.
- The Auth code is a 1 time usable code to establish a JWT with Auth 2.0.
- To establish a JWT: 
    - For private/public cookie method (Flask), the JWT requires the private key from the secure backend server. Therefore, the JWT's can only be created by the backend server (rather than a Auth code could be easily impersonated coming from multiple front end applications sent to the backend). 
    - For the shared JWT cookie key method (CLI), JWT's can be created by either parties. This makes it less secure than private/public. If someone were to get the JWT shared code, they could impersonate the user. To get the JWT code, this would require someone to scan your browser's cookie and retrieve it (which is possible in HTTPS cookies, but not HTTP cookies).
- To return:
    - For flask, it returns to the frontend URL's homepage for the user's login
    - For CLI, it returns to a browser with the JWT token

The user's homepage route
- Retrieves cookie from webbrowser
- Validates cookie by using the public key
- Redirects to user profile's html page

Logout
- Saves html as a rendering
- Save over old cookie jwt as a new cookie, with it expiring immediately
- Directs user to login page

## NOTES
- Creating coookies:
    - In general, there's two types of cookie keys for a JWT: private/public and shared.
    - The advantage to using shared is it's a little simpler (among others).
    - To generate the public key and then the private key, do the following in the console:
- Generating private/public keys:
    - Generate a 2048-bit RSA private key `openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048`
    - Generate the corresponding public key `openssl rsa -pubout -in private.pem -out public.pem`
