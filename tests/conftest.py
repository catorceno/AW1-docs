import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Todo, User
PASSWORD = "correct-horse-42"
@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        user = User(username="ana")
        user.set_password(PASSWORD)
        db.session.add(user)
        db.session.add(Todo(title="Primera tarea"))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token(client):
    """A real token through the login endpoint, like Postman would get it."""
    res = client.post("/auth/login", json={"username": "ana", "password": PASSWORD})
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]