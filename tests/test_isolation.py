from datetime import date
from app.extensions import db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense


def test_user_data_isolation(client, app):
    """Verify that users cannot view, edit, or delete another user's financial records"""
    with app.app_context():
        # Create User A
        user_a = User(name="User A", email="user_a@example.com")
        user_a.set_password("Pass123")
        db.session.add(user_a)

        # Create User B
        user_b = User(name="User B", email="user_b@example.com")
        user_b.set_password("Pass123")
        db.session.add(user_b)
        db.session.commit()

        # Add Income and Expense for User A
        inc_a = Income(amount=80000.0, source="Salary A", date=date.today(), description="Confidential Salary", user_id=user_a.id)
        exp_a = Expense(amount=12000.0, category="Rent", date=date.today(), description="Apartment A", user_id=user_a.id)
        db.session.add_all([inc_a, exp_a])
        db.session.commit()

        inc_a_id = inc_a.id
        exp_a_id = exp_a.id

    # Log in as User B
    client.post("/auth/login", data={"email": "user_b@example.com", "password": "Pass123"}, follow_redirects=True)

    # 1. User B accesses Income List -> Must NOT contain User A's income
    income_res = client.get("/income/")
    assert b"Salary A" not in income_res.data
    assert b"Confidential Salary" not in income_res.data

    # 2. User B accesses Expense List -> Must NOT contain User A's expense
    expense_res = client.get("/expense/")
    assert b"Apartment A" not in expense_res.data

    # 3. User B attempts to Edit User A's Income -> Must return 403 Forbidden
    edit_res = client.post(f"/income/edit/{inc_a_id}", data={
        "amount": "99999",
        "source": "Hacked",
        "date": "2026-10-01",
        "description": "Exploit"
    })
    assert edit_res.status_code == 403

    # 4. User B attempts to Delete User A's Income -> Must return 403 Forbidden
    del_res = client.post(f"/income/delete/{inc_a_id}")
    assert del_res.status_code == 403

    # Verify in DB that User A's record was untouched
    with app.app_context():
        intact_inc = db.session.get(Income, inc_a_id)
        assert intact_inc is not None
        assert intact_inc.amount == 80000.0
        assert intact_inc.source == "Salary A"
