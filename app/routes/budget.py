from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.budget import Budget
from app.models.expense import EXPENSE_CATEGORIES
from app.services.finance_analytics import get_budget_vs_actual

budget_bp = Blueprint("budget", __name__, url_prefix="/budget")


@budget_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    today = date.today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        try:
            monthly_budget = float(request.form.get("monthly_budget", 0))
            post_month = int(request.form.get("month", month))
            post_year = int(request.form.get("year", year))

            if monthly_budget < 0:
                flash("Budget amount cannot be negative.", "danger")
                return redirect(url_for("budget.index", month=post_month, year=post_year))

            if category not in EXPENSE_CATEGORIES:
                flash("Please select a valid expense category.", "danger")
                return redirect(url_for("budget.index", month=post_month, year=post_year))

            # Check if budget for this category/month/year already exists
            existing_budget = Budget.query.filter_by(
                user_id=current_user.id,
                category=category,
                month=post_month,
                year=post_year
            ).first()

            if existing_budget:
                existing_budget.monthly_budget = monthly_budget
                flash(f"Updated budget for {category} to ₹{monthly_budget:,.2f} for {date(post_year, post_month, 1).strftime('%B %Y')}.", "success")
            else:
                new_budget = Budget(
                    user_id=current_user.id,
                    category=category,
                    monthly_budget=monthly_budget,
                    month=post_month,
                    year=post_year
                )
                db.session.add(new_budget)
                flash(f"Set budget of ₹{monthly_budget:,.2f} for {category}.", "success")

            db.session.commit()
            return redirect(url_for("budget.index", month=post_month, year=post_year))

        except ValueError:
            flash("Invalid input values. Please enter a valid number.", "danger")
            return redirect(url_for("budget.index", month=month, year=year))

    # Get budget vs actual comparison data
    budget_report = get_budget_vs_actual(current_user.id, month, year)
    budgets_list = Budget.query.filter_by(user_id=current_user.id, month=month, year=year).all()

    # Generate list of years for selector
    years = list(range(today.year - 2, today.year + 3))

    return render_template(
        "budget/index.html",
        budget_report=budget_report,
        budgets_list=budgets_list,
        categories=EXPENSE_CATEGORIES,
        selected_month=month,
        selected_year=year,
        years=years,
        month_name=date(year, month, 1).strftime("%B %Y"),
    )


@budget_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    budget = db.session.get(Budget, id)
    if not budget:
        abort(404)
    if budget.user_id != current_user.id:
        abort(403)

    month = budget.month
    year = budget.year
    category = budget.category
    db.session.delete(budget)
    db.session.commit()
    flash(f"Removed budget for {category}.", "info")
    return redirect(url_for("budget.index", month=month, year=year))
