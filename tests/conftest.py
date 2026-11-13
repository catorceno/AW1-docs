"""Tests sign their own RS256 tokens and pose as Auth0.
No network and no Auth0 account are needed:
- the key client gets a key set built from a key pair generated here, so
verify_decode_jwt runs the same code it runs against the real JWKS;
- the OIDC discovery document is preloaded, so /auth/login can build the
Auth0 URL without downloading it.
"""
import json
import time
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Todo

KID = "test-key-1"
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
USER_PERMISSIONS = ["get:todos", "post:todos", "patch:todos"]
ADMIN_PERMISSIONS = USER_PERMISSIONS + ["delete:todos"]

def jwks(private_key=PRIVATE_KEY, kid=KID):
    """The public half, in the format Auth0 publishes it."""
    key = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    return {"keys": [{**key, "kid": kid, "use": "sig", "alg": "RS256"}]}

@pytest.fixture
def app():
    app = create_app(TestConfig)
    app.extensions["auth0_jwks"].fetch_data = lambda: jwks()
    domain = app.config["AUTH0_DOMAIN"]
    app.extensions["authlib.integrations.flask_client"].auth0.server_metadata.update({
        "issuer": f"https://{domain}/",
        "authorization_endpoint": f"https://{domain}/authorize",
        "token_endpoint": f"https://{domain}/oauth/token",
        "jwks_uri": f"https://{domain}/.well-known/jwks.json",
        "_loaded_at": time.time(),
    })
    with app.app_context():
        db.create_all()
        db.session.add(Todo(title="Primera tarea"))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def make_token(app):
    """Sign a token shaped like an Auth0 access token. Override any claim."""
    def _make(permissions=USER_PERMISSIONS, key=PRIVATE_KEY, kid=KID, algorithm="RS256", **claims):
        now = datetime.now(timezone.utc)
        payload = {
        "iss": f"https://{app.config['AUTH0_DOMAIN']}/",
        "sub": "auth0|ana",
        "aud": app.config["AUTH0_AUDIENCE"],
        "iat": now,
        "exp": now + timedelta(hours=1),
        "permissions": permissions,
        **claims,
        }
        if permissions is None:
            del payload["permissions"]
    
        return jwt.encode(payload, key, algorithm=algorithm, headers={"kid": kid})
    return _make

@pytest.fixture
def sign_in(client, make_token):
    """Put a token in the session, as /auth/callback does after a real login."""
    def _sign_in(permissions=USER_PERMISSIONS, name="Ana", **claims):
        with client.session_transaction() as session:
            session["access_token"] = make_token(permissions=permissions, **claims)
            session["user"] = {"name": name, "email": "ana@example.com"}
    return _sign_in