from datetime import date
from app.extensions import db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.savings import Savings
from app.services.finance_analytics import (
    get_user_overview,
    get_category_breakdown,
    get_budget_vs_actual,
    get_monthly_trends,
    get_financial_health_score,
)


def test_financial_analytics_calculations(app):
    """Test financial summaries, variances, and health score calculations"""
    with app.app_context():
        # Create user
        user = User(name="Calc User", email="calc@example.com")
        user.set_password("Pass123")
        db.session.add(user)
        db.session.commit()

        today = date.today()

        # Add Income: 100,000
        db.session.add(Income(amount=100000.0, source="Salary", date=today, user_id=user.id))

        # Add Expenses: Rent 30000, Food 15000, Shopping 10000
        db.session.add(Expense(amount=30000.0, category="Rent", date=today, user_id=user.id))
        db.session.add(Expense(amount=15000.0, category="Food", date=today, user_id=user.id))
        db.session.add(Expense(amount=10000.0, category="Shopping", date=today, user_id=user.id))

        # Add Budget: Food 12000 (spent 15000 -> over budget by 3000), Rent 30000 (spent 30000)
        db.session.add(Budget(category="Food", monthly_budget=12000.0, month=today.month, year=today.year, user_id=user.id))
        db.session.add(Budget(category="Rent", monthly_budget=30000.0, month=today.month, year=today.year, user_id=user.id))

        # Add Savings deposit: 25000
        db.session.add(Savings(amount=25000.0, date=today, notes="Mutual Fund SIP", user_id=user.id))

        db.session.commit()

        # 1. Test Overview
        overview = get_user_overview(user.id)
        assert overview["total_income"] == 100000.0
        assert overview["total_expense"] == 55000.0
        assert overview["net_balance"] == 45000.0
        assert overview["current_savings"] == 25000.0
        assert overview["month_balance"] == 45000.0

        # 2. Test Category Breakdown
        breakdown = get_category_breakdown(user.id, today.month, today.year)
        assert breakdown["total"] == 55000.0
        rent_item = next(item for item in breakdown["items"] if item["category"] == "Rent")
        assert rent_item["amount"] == 30000.0
        assert rent_item["percentage"] == round(30000 / 55000 * 100, 1)

        # 3. Test Budget vs Actual
        b_vs_a = get_budget_vs_actual(user.id, today.month, today.year)
        assert b_vs_a["total_budgeted"] == 42000.0
        assert b_vs_a["total_spent"] == 55000.0
        food_b = next(c for c in b_vs_a["categories"] if c["category"] == "Food")
        assert food_b["is_overspent"] is True
        assert food_b["spent"] == 15000.0
        assert food_b["remaining"] == -3000.0

        # 4. Test Trends
        trends = get_monthly_trends(user.id, num_months=6)
        assert len(trends["labels"]) == 6
        assert trends["income"][-1] == 100000.0
        assert trends["expenses"][-1] == 55000.0
        assert trends["savings"][-1] == 25000.0

        # 5. Test Financial Health Score
        health = get_financial_health_score(user.id)
        assert 0 <= health["score"] <= 100
        assert health["rating"] in ["Excellent", "Good", "Fair", "Needs Attention"]
