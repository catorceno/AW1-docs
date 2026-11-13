import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # Signs the session cookie, which holds the Auth0 access token after login.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me") # firma la cookie de sesión
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://todo:todo@localhost:5432/todoapp",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # The session cookie: JavaScript cannot read it, other sites' forms do not
    # carry it, and in production it only travels over HTTPS.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    
    # 1 behind nginx: trust its X-Forwarded-Proto and Host headers, so the
    # callback URL sent to Auth0 says https://your-domain and not http://web:5000.
    BEHIND_PROXY = os.environ.get("BEHIND_PROXY", "0") == "1"
    
    # Auth0. The client secret proves to Auth0 that the server is this app:
    # it lives only in the environment, never in the code or the browser.
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "") # your-tenant.us.auth0.com
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "") # the API Identifier
    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "") # the Regular Web Application
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET", "")

class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    AUTH0_DOMAIN = "test-tenant.us.auth0.com"
    AUTH0_AUDIENCE = "todoapp-api"
    AUTH0_CLIENT_ID = "test-client-id"
    AUTH0_CLIENT_SECRET = "test-client-secret"
