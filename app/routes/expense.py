from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.expense import Expense, EXPENSE_CATEGORIES

expense_bp = Blueprint("expense", __name__, url_prefix="/expense")


@expense_bp.route("/")
@login_required
def index():
    category_filter = request.args.get("category", "")
    query = Expense.query.filter_by(user_id=current_user.id)

    if category_filter and category_filter in EXPENSE_CATEGORIES:
        query = query.filter_by(category=category_filter)

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total_expense = sum(e.amount for e in expenses)

    return render_template(
        "expense/index.html",
        expenses=expenses,
        total_expense=total_expense,
        categories=EXPENSE_CATEGORIES,
        selected_category=category_filter,
    )


@expense_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            category = request.form.get("category", "").strip()
            date_str = request.form.get("date", "")
            description = request.form.get("description", "").strip()

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return render_template("expense/form.html", categories=EXPENSE_CATEGORIES, today=date.today())

            if category not in EXPENSE_CATEGORIES:
                flash("Please choose a valid expense category.", "danger")
                return render_template("expense/form.html", categories=EXPENSE_CATEGORIES, today=date.today())

            expense_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

            new_expense = Expense(
                amount=amount,
                category=category,
                date=expense_date,
                description=description,
                user_id=current_user.id,
            )
            db.session.add(new_expense)
            db.session.commit()

            flash(f"Expense of ₹{amount:,.2f} under {category} recorded!", "success")
            return redirect(url_for("expense.index"))

        except ValueError:
            flash("Invalid input values. Please verify the amount and date.", "danger")

    return render_template("expense/form.html", categories=EXPENSE_CATEGORIES, today=date.today(), expense=None)


@expense_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    expense = db.session.get(Expense, id)
    if not expense:
        abort(404)
    if expense.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            category = request.form.get("category", "").strip()
            date_str = request.form.get("date", "")
            description = request.form.get("description", "").strip()

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return render_template("expense/form.html", categories=EXPENSE_CATEGORIES, expense=expense)

            if category not in EXPENSE_CATEGORIES:
                flash("Please choose a valid expense category.", "danger")
                return render_template("expense/form.html", categories=EXPENSE_CATEGORIES, expense=expense)

            expense.amount = amount
            expense.category = category
            expense.date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else expense.date
            expense.description = description

            db.session.commit()
            flash("Expense record updated successfully!", "success")
            return redirect(url_for("expense.index"))

        except ValueError:
            flash("Invalid input values.", "danger")

    return render_template("expense/form.html", categories=EXPENSE_CATEGORIES, expense=expense)


@expense_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    expense = db.session.get(Expense, id)
    if not expense:
        abort(404)
    if expense.user_id != current_user.id:
        abort(403)

    amount = expense.amount
    cat = expense.category
    db.session.delete(expense)
    db.session.commit()
    flash(f"Expense (₹{amount:,.2f} - {cat}) deleted.", "info")
    return redirect(url_for("expense.index"))
