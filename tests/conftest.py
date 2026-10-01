import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a testing Flask app instance with in-memory SQLite"""
    flask_app = create_app("testing")
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """Test client with a pre-registered and logged in user"""
    with app.app_context():
        user = User(name="Test User", email="test@example.com")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

    # Log the user in
    client.post("/auth/login", data={"email": "test@example.com", "password": "Password123"}, follow_redirects=True)
    return client
