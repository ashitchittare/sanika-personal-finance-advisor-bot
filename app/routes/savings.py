from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.extensions import db
from app.models.savings import Savings
from app.services.finance_analytics import get_user_overview, get_monthly_trends

savings_bp = Blueprint("savings", __name__, url_prefix="/savings")


@savings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    today = date.today()
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            date_str = request.form.get("date", "")
            notes = request.form.get("notes", "").strip()

            if amount <= 0:
                flash("Savings deposit amount must be greater than zero.", "danger")
                return redirect(url_for("savings.index"))

            savings_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else today

            new_savings = Savings(
                amount=amount,
                date=savings_date,
                notes=notes,
                user_id=current_user.id
            )
            db.session.add(new_savings)
            db.session.commit()

            flash(f"Deposited ₹{amount:,.2f} into savings successfully!", "success")
            return redirect(url_for("savings.index"))

        except ValueError:
            flash("Invalid input values. Please check amount and date format.", "danger")
            return redirect(url_for("savings.index"))

    savings_list = Savings.query.filter_by(user_id=current_user.id).order_by(Savings.date.desc(), Savings.id.desc()).all()
    overview = get_user_overview(current_user.id)
    trends = get_monthly_trends(current_user.id, num_months=6)

    # Calculate this month's savings deposits
    month_savings_total = db.session.query(func.coalesce(func.sum(Savings.amount), 0.0)).filter(
        Savings.user_id == current_user.id,
        extract("month", Savings.date) == today.month,
        extract("year", Savings.date) == today.year
    ).scalar()

    return render_template(
        "savings/index.html",
        savings_list=savings_list,
        overview=overview,
        trends=trends,
        month_savings_total=month_savings_total,
        today=today,
    )


@savings_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    saving = db.session.get(Savings, id)
    if not saving:
        abort(404)
    if saving.user_id != current_user.id:
        abort(403)

    amt = saving.amount
    db.session.delete(saving)
    db.session.commit()
    flash(f"Removed savings entry of ₹{amt:,.2f}.", "info")
    return redirect(url_for("savings.index"))
