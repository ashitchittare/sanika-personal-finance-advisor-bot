from datetime import date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.income import Income
from app.models.expense import Expense
from app.models.goal import FinancialGoal
from app.services.finance_analytics import (
    get_user_overview,
    get_category_breakdown,
    get_monthly_trends,
    get_financial_health_score,
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/dashboard")
@login_required
def index():
    today = date.today()
    overview = get_user_overview(current_user.id)
    category_data = get_category_breakdown(current_user.id, today.month, today.year)
    trends = get_monthly_trends(current_user.id, num_months=6)
    health = get_financial_health_score(current_user.id)
    goals = FinancialGoal.query.filter_by(user_id=current_user.id).order_by(FinancialGoal.target_date.asc()).limit(3).all()

    # Fetch recent transactions (Incomes and Expenses combined)
    recent_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc(), Income.id.desc()).limit(10).all()
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc(), Expense.id.desc()).limit(10).all()

    transactions = []
    for inc in recent_incomes:
        transactions.append({
            "id": inc.id,
            "type": "Income",
            "title": inc.source,
            "category_or_source": inc.source,
            "amount": inc.amount,
            "date": inc.date,
            "description": inc.description or "",
            "is_income": True,
        })
    for exp in recent_expenses:
        transactions.append({
            "id": exp.id,
            "type": "Expense",
            "title": exp.category,
            "category_or_source": exp.category,
            "amount": exp.amount,
            "date": exp.date,
            "description": exp.description or "",
            "is_income": False,
        })

    # Sort combined transactions by date desc
    transactions.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
    recent_transactions = transactions[:8]

    return render_template(
        "dashboard.html",
        overview=overview,
        category_data=category_data,
        trends=trends,
        health=health,
        goals=goals,
        recent_transactions=recent_transactions,
    )
