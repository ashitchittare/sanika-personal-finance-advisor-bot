from datetime import date, datetime, timedelta
from calendar import monthrange
from sqlalchemy import func, extract
from app.extensions import db
from app.models.income import Income
from app.models.expense import Expense, EXPENSE_CATEGORIES
from app.models.budget import Budget
from app.models.savings import Savings
from app.models.goal import FinancialGoal


def get_user_overview(user_id: int):
    """
    Computes overall all-time and current month financial summaries for the given user.
    """
    today = date.today()
    current_month = today.month
    current_year = today.year

    # All-time totals
    total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == user_id
    ).scalar()

    total_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == user_id
    ).scalar()

    total_savings_deposits = db.session.query(func.coalesce(func.sum(Savings.amount), 0.0)).filter(
        Savings.user_id == user_id
    ).scalar()

    net_balance = round(total_income - total_expense, 2)
    # Total accumulated savings is manual savings logs or calculated positive balance
    current_savings = round(total_savings_deposits, 2)

    # Current month metrics
    month_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == user_id,
        extract("month", Income.date) == current_month,
        extract("year", Income.date) == current_year,
    ).scalar()

    month_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == user_id,
        extract("month", Expense.date) == current_month,
        extract("year", Expense.date) == current_year,
    ).scalar()

    month_savings = db.session.query(func.coalesce(func.sum(Savings.amount), 0.0)).filter(
        Savings.user_id == user_id,
        extract("month", Savings.date) == current_month,
        extract("year", Savings.date) == current_year,
    ).scalar()

    month_balance = round(month_income - month_expense, 2)

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "current_savings": current_savings,
        "net_balance": net_balance,
        "month_income": round(month_income, 2),
        "month_expense": round(month_expense, 2),
        "month_savings": round(month_savings, 2),
        "month_balance": month_balance,
        "current_month": current_month,
        "current_year": current_year,
        "month_name": today.strftime("%B %Y"),
    }


def get_category_breakdown(user_id: int, month: int = None, year: int = None):
    """
    Returns breakdown of expenses by category with total amount and percentage.
    """
    query = db.session.query(
        Expense.category,
        func.coalesce(func.sum(Expense.amount), 0.0).label("total")
    ).filter(Expense.user_id == user_id)

    if month and year:
        query = query.filter(
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year
        )
    elif year:
        query = query.filter(extract("year", Expense.date) == year)

    results = query.group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    total_exp = sum(r.total for r in results)
    breakdown = []
    
    # Preset color mapping for Chart.js
    category_colors = {
        "Food": "#FF6384",
        "Transport": "#36A2EB",
        "Education": "#FFCE56",
        "Rent": "#4BC0C0",
        "Shopping": "#9966FF",
        "Entertainment": "#FF9F40",
        "Healthcare": "#E74C3C",
        "Bills": "#2ECC71",
        "Other": "#95A5A6",
    }

    for cat, amount in results:
        pct = round((amount / total_exp * 100), 1) if total_exp > 0 else 0
        breakdown.append({
            "category": cat,
            "amount": round(amount, 2),
            "percentage": pct,
            "color": category_colors.get(cat, "#3b82f6"),
        })

    # Include any zero-expense standard categories if needed
    existing_cats = {b["category"] for b in breakdown}
    for cat in EXPENSE_CATEGORIES:
        if cat not in existing_cats:
            breakdown.append({
                "category": cat,
                "amount": 0.0,
                "percentage": 0.0,
                "color": category_colors.get(cat, "#94a3b8"),
            })

    return {
        "items": breakdown,
        "total": round(total_exp, 2),
        "labels": [b["category"] for b in breakdown if b["amount"] > 0] or ["No Expenses"],
        "data": [b["amount"] for b in breakdown if b["amount"] > 0] or [0],
        "colors": [b["color"] for b in breakdown if b["amount"] > 0] or ["#94a3b8"],
    }


def get_budget_vs_actual(user_id: int, month: int, year: int):
    """
    Computes planned budget vs actual spending for each category in the specified month.
    """
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    budget_map = {b.category: b.monthly_budget for b in budgets}

    # Query actual spending in that month
    actuals = db.session.query(
        Expense.category,
        func.coalesce(func.sum(Expense.amount), 0.0).label("total")
    ).filter(
        Expense.user_id == user_id,
        extract("month", Expense.date) == month,
        extract("year", Expense.date) == year
    ).group_by(Expense.category).all()
    actual_map = {a.category: a.total for a in actuals}

    report = []
    total_budgeted = 0.0
    total_spent = 0.0
    overspent_count = 0

    # Evaluate categories that have a budget or actual spend
    all_categories = sorted(list(set(list(budget_map.keys()) + list(actual_map.keys()) + EXPENSE_CATEGORIES)))

    for cat in all_categories:
        budget_amt = budget_map.get(cat, 0.0)
        spent_amt = actual_map.get(cat, 0.0)
        remaining = budget_amt - spent_amt
        pct_used = round((spent_amt / budget_amt * 100), 1) if budget_amt > 0 else (100.0 if spent_amt > 0 else 0.0)
        is_over = spent_amt > budget_amt if budget_amt > 0 else (spent_amt > 0)

        if is_over:
            overspent_count += 1

        total_budgeted += budget_amt
        total_spent += spent_amt

        report.append({
            "category": cat,
            "budget": round(budget_amt, 2),
            "spent": round(spent_amt, 2),
            "remaining": round(remaining, 2),
            "percentage": pct_used,
            "is_overspent": is_over,
            "has_budget": budget_amt > 0,
        })

    return {
        "categories": report,
        "total_budgeted": round(total_budgeted, 2),
        "total_spent": round(total_spent, 2),
        "total_remaining": round(total_budgeted - total_spent, 2),
        "overspent_count": overspent_count,
        "month": month,
        "year": year,
    }


def get_monthly_trends(user_id: int, num_months: int = 6):
    """
    Computes monthly income, expense, and savings trends for the last N months.
    """
    today = date.today()
    labels = []
    income_data = []
    expense_data = []
    savings_data = []

    # Generate chronologically ascending list of months
    for i in range(num_months - 1, -1, -1):
        # Calculate target month and year
        target_year = today.year
        target_month = today.month - i
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        month_label = date(target_year, target_month, 1).strftime("%b %Y")
        labels.append(month_label)

        inc = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
            Income.user_id == user_id,
            extract("month", Income.date) == target_month,
            extract("year", Income.date) == target_year,
        ).scalar()

        exp = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.user_id == user_id,
            extract("month", Expense.date) == target_month,
            extract("year", Expense.date) == target_year,
        ).scalar()

        sav = db.session.query(func.coalesce(func.sum(Savings.amount), 0.0)).filter(
            Savings.user_id == user_id,
            extract("month", Savings.date) == target_month,
            extract("year", Savings.date) == target_year,
        ).scalar()

        income_data.append(round(inc, 2))
        expense_data.append(round(exp, 2))
        savings_data.append(round(sav, 2))

    return {
        "labels": labels,
        "income": income_data,
        "expenses": expense_data,
        "savings": savings_data,
    }


def get_financial_health_score(user_id: int):
    """
    Computes a 0-100 financial health score based on savings rate, budget discipline, and goal progress.
    """
    overview = get_user_overview(user_id)
    inc = overview["month_income"] if overview["month_income"] > 0 else overview["total_income"]
    exp = overview["month_expense"] if overview["month_expense"] > 0 else overview["total_expense"]
    
    score = 50  # Base neutral score
    insights = []

    # 1. Savings Ratio (Up to +25 or -20)
    if inc > 0:
        savings_ratio = (inc - exp) / inc
        if savings_ratio >= 0.30:
            score += 25
            insights.append("Outstanding savings rate (>30% of income).")
        elif savings_ratio >= 0.20:
            score += 18
            insights.append("Healthy savings rate (20-30% of income).")
        elif savings_ratio >= 0.05:
            score += 8
            insights.append("Modest positive savings rate (5-20%).")
        elif savings_ratio < 0:
            score -= 20
            insights.append("Warning: Expenses currently exceed income.")
    else:
        insights.append("No active monthly income recorded.")

    # 2. Budget adherence (+15 or -15)
    today = date.today()
    budget_info = get_budget_vs_actual(user_id, today.month, today.year)
    if budget_info["total_budgeted"] > 0:
        if budget_info["overspent_count"] == 0:
            score += 15
            insights.append("All spending is strictly within planned budgets.")
        elif budget_info["overspent_count"] <= 2:
            score += 5
            insights.append(f"{budget_info['overspent_count']} budget category exceeded.")
        else:
            score -= 15
            insights.append(f"Multiple categories ({budget_info['overspent_count']}) over budget.")
    else:
        insights.append("No monthly budget set yet. Create budgets to improve score.")

    # 3. Goals Progress (+10)
    goals = FinancialGoal.query.filter_by(user_id=user_id).all()
    if goals:
        completed = sum(1 for g in goals if g.is_completed)
        avg_progress = sum(g.progress_percentage for g in goals) / len(goals)
        if avg_progress >= 50 or completed > 0:
            score += 10
            insights.append(f"Strong goal momentum (Avg progress: {round(avg_progress, 1)}%).")
        else:
            score += 5
            insights.append("Active financial goals in progress.")

    score = max(5, min(100, score))
    
    if score >= 80:
        rating = "Excellent"
        rating_color = "success"
    elif score >= 60:
        rating = "Good"
        rating_color = "primary"
    elif score >= 40:
        rating = "Fair"
        rating_color = "warning"
    else:
        rating = "Needs Attention"
        rating_color = "danger"

    return {
        "score": score,
        "rating": rating,
        "color": rating_color,
        "insights": insights,
    }
