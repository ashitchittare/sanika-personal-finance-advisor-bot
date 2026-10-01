from app.models.user import User


def test_user_registration(client, app):
    """Test successful user registration"""
    response = client.post("/auth/register", data={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome to FinBot" in response.data

    with app.app_context():
        user = User.query.filter_by(email="jane@example.com").first()
        assert user is not None
        assert user.name == "Jane Doe"
        assert user.check_password("Password123")
        assert not user.check_password("WrongPassword")


def test_registration_password_mismatch(client):
    """Test registration failure when passwords do not match"""
    response = client.post("/auth/register", data={
        "name": "Jane Doe",
        "email": "jane2@example.com",
        "password": "Password123",
        "confirm_password": "DifferentPassword",
    }, follow_redirects=True)

    assert b"Passwords do not match" in response.data


def test_user_login_and_logout(client, app):
    """Test login and logout flow"""
    # Create user
    with app.app_context():
        user = User(name="John Doe", email="john@example.com")
        user.set_password("Secret123")
        from app.extensions import db
        db.session.add(user)
        db.session.commit()

    # Successful login
    login_res = client.post("/auth/login", data={
        "email": "john@example.com",
        "password": "Secret123"
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Financial Dashboard" in login_res.data

    # Logout
    logout_res = client.get("/auth/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"logged out successfully" in logout_res.data


def test_protected_routes(client):
    """Test that unauthenticated requests redirect to login"""
    for route in ["/dashboard", "/income/", "/expense/", "/budget/", "/savings/", "/goals/", "/reports/", "/finbot/"]:
        res = client.get(route, follow_redirects=False)
        assert res.status_code in [302, 308]
        assert "/auth/login" in res.headers["Location"]
