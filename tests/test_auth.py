from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from app import create_app
from app.auth.oauth import auth0
from app.config import TestConfig
from app.extensions import db
from app.models import Todo
from tests.conftest import ADMIN_PERMISSIONS, USER_PERMISSIONS

def past(hours):
    return datetime.now(timezone.utc) - timedelta(hours=hours)

# ---------------------------------------------------------------- login flow
def test_without_session_the_page_offers_to_sign_in(client):
    res = client.get("/")
    assert res.status_code == 401
    page = res.get_data(as_text=True)
    assert "Sign in with Auth0" in page
    assert "Primera tarea" not in page

def test_login_redirects_to_auth0_with_the_audience(client):
    res = client.get("/auth/login?next=/todos/1/edit")
    assert res.status_code == 302
    url = urlparse(res.headers["Location"])
    params = parse_qs(url.query)
    assert url.netloc == "test-tenant.us.auth0.com" and url.path == "/authorize"
    assert params["audience"] == ["todoapp-api"]
    assert params["client_id"] == ["test-client-id"]
    assert params["response_type"] == ["code"]
    assert params["redirect_uri"] == ["http://localhost/auth/callback"]
    assert params["state"][0] # Authlib checks it on the way back
    with client.session_transaction() as session:
        assert session["next"] == "/todos/1/edit"

def test_callback_saves_the_token_and_returns_to_next(app, client, make_token, monkeypatch):
    token = make_token()
    with client.session_transaction() as session:
        session["next"] = "/todos/1/edit"
        session["leftover"] = "from before the login"
    with app.test_request_context():
        monkeypatch.setattr(type(auth0()), "authorize_access_token",
                            lambda self, **kw: {"access_token": token, "userinfo": {"name": "Ana", "email": "ana@example.com"}})
    
    res = client.get("/auth/callback?code=abc&state=xyz")
    assert res.status_code == 302
    assert res.headers["Location"] == "/todos/1/edit"
    with client.session_transaction() as session:
        assert session["access_token"] == token
        assert session["user"]["name"] == "Ana"
        assert "leftover" not in session # a new login starts a new session
    assert "Primera tarea" in client.get("/").get_data(as_text=True)

def test_callback_error_from_auth0_is_shown(app, client, monkeypatch):
    from authlib.integrations.base_client.errors import OAuthError
    def deny(self, **kw):
        raise OAuthError(error="access_denied", description="User did not authorize the request")
    
    with app.test_request_context():
        monkeypatch.setattr(type(auth0()), "authorize_access_token", deny)
    
    res = client.get("/auth/callback?error=access_denied", follow_redirects=True)
    assert "User did not authorize the request" in res.get_data(as_text=True)
    with client.session_transaction() as session:
        assert "access_token" not in session

@pytest.mark.parametrize("target", ["//evil.example", "https://evil.example", "/\\evil.example"])
def test_login_does_not_open_redirect(client, target):
    client.get(f"/auth/login?next={target}")
    with client.session_transaction() as session:
        assert session["next"] == "/"

def test_logout_clears_the_session_and_closes_auth0(client, sign_in):
    sign_in()
    res = client.post("/auth/logout")
    url = urlparse(res.headers["Location"])
    assert url.netloc == "test-tenant.us.auth0.com" and url.path == "/v2/logout"
    assert parse_qs(url.query)["returnTo"] == ["http://localhost/"]
    with client.session_transaction() as session:
        assert "access_token" not in session

def test_session_cookie_is_httponly_and_samesite(client, app, make_token, monkeypatch):
    with app.test_request_context():
        monkeypatch.setattr(type(auth0()), "authorize_access_token",
                            lambda self, **kw: {"access_token": make_token(), "userinfo": {}})
    res = client.get("/auth/callback?code=abc")
    cookie = res.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie

# ---------------------------------------------------------------- the three filters
@pytest.mark.parametrize("permissions, status", [(None, 401), (USER_PERMISSIONS, 403), (ADMIN_PERMISSIONS, 302)])
def test_delete_matrix(client, sign_in, permissions, status):
    if permissions is not None:
        sign_in(permissions=permissions)
    assert client.post("/todos/1/delete").status_code == status

def test_hidden_button_is_not_the_protection(client, sign_in):
    """The user cannot see the button, but posting directly must still fail."""
    sign_in()
    assert "btn-danger" not in client.get("/").get_data(as_text=True)
    res = client.post("/todos/1/delete")
    assert res.status_code == 403
    assert db.session.get(Todo, 1) is not None

def test_admin_sees_and_uses_delete(client, sign_in):  
    sign_in(permissions=ADMIN_PERMISSIONS)
    assert "btn-danger" in client.get("/").get_data(as_text=True)
    client.post("/todos/1/delete")
    assert db.session.get(Todo, 1) is None

def test_user_can_create_toggle_and_edit(client, sign_in):
    sign_in()
    client.post("/todos", data={"title": "Desde el formulario"})
    client.post("/todos/1/toggle")
    client.post("/todos/1/edit", data={"title": "Renombrada", "description": ""})
    page = client.get("/").get_data(as_text=True)
    assert "Desde el formulario" in page and "Renombrada" in page
    assert db.session.get(Todo, 1).completed is True

# ---------------------------------------------------------------- verify_decode_jwt
@pytest.mark.parametrize("claims", [
    {"iat": past(2), "exp": past(1)},
    {"aud": "another-api"},
    {"iss": "https://someone-else.auth0.com/"},
])
def test_bad_tokens_in_the_session_ask_to_sign_in_again(client, sign_in, claims):
    sign_in(**claims)
    res = client.get("/")
    assert res.status_code == 401
    assert "Sign in with Auth0" in res.get_data(as_text=True)
    with client.session_transaction() as session:
        assert "access_token" not in session

def test_token_signed_by_another_key_is_rejected(client, make_token):
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with client.session_transaction() as session:
        session["access_token"] = make_token(key=attacker_key, permissions=ADMIN_PERMISSIONS)
    assert client.post("/todos/1/delete").status_code == 401

def test_hs256_token_is_rejected(client, make_token):
    with client.session_transaction() as session:
        session["access_token"] = make_token(key="a-shared-secret-that-is-32-bytes-long", algorithm="HS256")
    assert client.get("/").status_code == 401

def test_missing_permissions_claim_is_a_400(client, sign_in):
    """What the app sees when RBAC is not enabled on the Auth0 API."""
    sign_in(permissions=None)
    res = client.get("/")
    assert res.status_code == 400
    assert "Permissions not included" in res.get_data(as_text=True)

def test_auth0_unreachable_is_a_503(app, client, sign_in):
    def offline():
        raise jwt.PyJWKClientConnectionError("Fail to fetch data from the url")
    app.extensions["auth0_jwks"].fetch_data = offline
    sign_in()
    assert client.get("/").status_code == 503

# ---------------------------------------------------------------- config
def test_app_refuses_to_start_without_the_client_secret():
    class NoSecret(TestConfig):
        AUTH0_CLIENT_SECRET = ""

    with pytest.raises(RuntimeError, match="AUTH0_CLIENT_SECRET"):
        create_app(NoSecret)

def test_behind_proxy_the_callback_uses_the_public_url():
    class Proxied(TestConfig):
        BEHIND_PROXY = True

    app = create_app(Proxied)
    app.extensions["authlib.integrations.flask_client"].auth0.server_metadata.update({
        "authorization_endpoint": "https://test-tenant.us.auth0.com/authorize", "_loaded_at": 1,
    })
    res = app.test_client().get("/auth/login", headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "todo.example.com"})
    redirect_uri = parse_qs(urlparse(res.headers["Location"]).query)["redirect_uri"]
    assert redirect_uri == ["https://todo.example.com/auth/callback"]