from datetime import date
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.savings import Savings
from app.models.goal import FinancialGoal


def test_income_crud(auth_client, app):
    """Test Income creation, editing, and deletion"""
    # 1. Create Income
    create_res = auth_client.post("/income/add", data={
        "amount": "50000",
        "source": "Salary",
        "date": "2026-10-01",
        "description": "Monthly engineering salary"
    }, follow_redirects=True)
    assert create_res.status_code == 200
    assert b"Salary" in create_res.data

    with app.app_context():
        inc = Income.query.filter_by(source="Salary").first()
        assert inc is not None
        assert inc.amount == 50000.0
        income_id = inc.id

    # 2. Edit Income
    edit_res = auth_client.post(f"/income/edit/{income_id}", data={
        "amount": "55000",
        "source": "Salary",
        "date": "2026-10-01",
        "description": "Salary with bonus"
    }, follow_redirects=True)
    assert edit_res.status_code == 200

    with app.app_context():
        updated_inc = db.session.get(Income, income_id)
        assert updated_inc.amount == 55000.0
        assert updated_inc.description == "Salary with bonus"

    # 3. Delete Income
    del_res = auth_client.post(f"/income/delete/{income_id}", follow_redirects=True)
    assert del_res.status_code == 200

    with app.app_context():
        assert db.session.get(Income, income_id) is None


def test_expense_crud(auth_client, app):
    """Test Expense creation, editing, and deletion"""
    # 1. Create Expense
    create_res = auth_client.post("/expense/add", data={
        "amount": "3200",
        "category": "Food",
        "date": "2026-10-01",
        "description": "Grocery shopping"
    }, follow_redirects=True)
    assert create_res.status_code == 200

    with app.app_context():
        exp = Expense.query.filter_by(category="Food").first()
        assert exp is not None
        assert exp.amount == 3200.0
        expense_id = exp.id

    # 2. Edit Expense
    edit_res = auth_client.post(f"/expense/edit/{expense_id}", data={
        "amount": "3500",
        "category": "Food",
        "date": "2026-10-01",
        "description": "Grocery & snacks"
    }, follow_redirects=True)
    assert edit_res.status_code == 200

    with app.app_context():
        updated_exp = db.session.get(Expense, expense_id)
        assert updated_exp.amount == 3500.0

    # 3. Delete Expense
    del_res = auth_client.post(f"/expense/delete/{expense_id}", follow_redirects=True)
    assert del_res.status_code == 200

    with app.app_context():
        assert db.session.get(Expense, expense_id) is None


def test_budget_management(auth_client, app):
    """Test setting, updating, and removing monthly category budgets"""
    # 1. Set Budget
    res = auth_client.post("/budget/", data={
        "category": "Food",
        "monthly_budget": "12000",
        "month": "10",
        "year": "2026",
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        b = Budget.query.filter_by(category="Food", month=10, year=2026).first()
        assert b is not None
        assert b.monthly_budget == 12000.0
        b_id = b.id

    # 2. Update Budget
    res2 = auth_client.post("/budget/", data={
        "category": "Food",
        "monthly_budget": "14000",
        "month": "10",
        "year": "2026",
    }, follow_redirects=True)
    assert res2.status_code == 200

    with app.app_context():
        b_updated = db.session.get(Budget, b_id)
        assert b_updated.monthly_budget == 14000.0

    # 3. Delete Budget
    del_res = auth_client.post(f"/budget/delete/{b_id}", follow_redirects=True)
    assert del_res.status_code == 200
    with app.app_context():
        assert db.session.get(Budget, b_id) is None


def test_savings_and_goals_crud(auth_client, app):
    """Test savings deposit and financial goals milestone progress"""
    # 1. Savings Deposit
    sav_res = auth_client.post("/savings/", data={
        "amount": "15000",
        "date": "2026-10-01",
        "notes": "SIP Mutual Fund"
    }, follow_redirects=True)
    assert sav_res.status_code == 200

    with app.app_context():
        sav = Savings.query.filter_by(notes="SIP Mutual Fund").first()
        assert sav is not None
        assert sav.amount == 15000.0
        sav_id = sav.id

    # 2. Goal Creation
    goal_res = auth_client.post("/goals/", data={
        "title": "MacBook Pro",
        "target_amount": "100000",
        "current_amount": "20000",
        "target_date": "2026-12-31"
    }, follow_redirects=True)
    assert goal_res.status_code == 200

    with app.app_context():
        goal = FinancialGoal.query.filter_by(title="MacBook Pro").first()
        assert goal is not None
        assert goal.progress_percentage == 20.0
        assert not goal.is_completed
        goal_id = goal.id

    # 3. Update Goal Progress
    prog_res = auth_client.post(f"/goals/update-progress/{goal_id}", data={
        "add_amount": "80000"
    }, follow_redirects=True)
    assert prog_res.status_code == 200

    with app.app_context():
        goal_done = db.session.get(FinancialGoal, goal_id)
        assert goal_done.current_amount == 100000.0
        assert goal_done.progress_percentage == 100.0
        assert goal_done.is_completed

    # 4. Delete Goal
    del_res = auth_client.post(f"/goals/delete/{goal_id}", follow_redirects=True)
    assert del_res.status_code == 200
    with app.app_context():
        assert db.session.get(FinancialGoal, goal_id) is None
