from datetime import date
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense
from app.models.savings import Savings
from app.services.finance_analytics import (
    get_category_breakdown,
    get_budget_vs_actual,
    get_monthly_trends,
    get_financial_health_score,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def index():
    today = date.today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))

    # Calculate month metrics
    month_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == current_user.id,
        extract("month", Income.date) == month,
        extract("year", Income.date) == year
    ).scalar()

    month_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == current_user.id,
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year
    ).scalar()

    month_savings = db.session.query(func.coalesce(func.sum(Savings.amount), 0.0)).filter(
        Savings.user_id == current_user.id,
        extract("month", Savings.date) == month,
        extract("year", Savings.date) == year
    ).scalar()

    net_balance = month_income - month_expense

    # Category breakdown for this selected month/year
    category_data = get_category_breakdown(current_user.id, month, year)
    budget_report = get_budget_vs_actual(current_user.id, month, year)
    trends = get_monthly_trends(current_user.id, num_months=12)
    health = get_financial_health_score(current_user.id)

    years = list(range(today.year - 3, today.year + 2))
    month_name = date(year, month, 1).strftime("%B %Y")

    return render_template(
        "reports/index.html",
        month_income=round(month_income, 2),
        month_expense=round(month_expense, 2),
        month_savings=round(month_savings, 2),
        net_balance=round(net_balance, 2),
        category_data=category_data,
        budget_report=budget_report,
        trends=trends,
        health=health,
        selected_month=month,
        selected_year=year,
        years=years,
        month_name=month_name,
    )


@reports_bp.route("/api/chart-data")
@login_required
def chart_data():
    """API endpoint to supply dynamic data for frontend charts"""
    today = date.today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))

    category_data = get_category_breakdown(current_user.id, month, year)
    trends = get_monthly_trends(current_user.id, num_months=6)
    budget_report = get_budget_vs_actual(current_user.id, month, year)

    return jsonify({
        "categories": category_data,
        "trends": trends,
        "budget": budget_report,
    })
