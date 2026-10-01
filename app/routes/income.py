from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.income import Income

income_bp = Blueprint("income", __name__, url_prefix="/income")

INCOME_SOURCES = ["Salary", "Freelance", "Investments", "Business", "Rental", "Bonus", "Gift", "Other"]


@income_bp.route("/")
@login_required
def index():
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc(), Income.id.desc()).all()
    total_income = sum(i.amount for i in incomes)
    return render_template("income/index.html", incomes=incomes, total_income=total_income, sources=INCOME_SOURCES)


@income_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            source = request.form.get("source", "").strip()
            date_str = request.form.get("date", "")
            description = request.form.get("description", "").strip()

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return render_template("income/form.html", sources=INCOME_SOURCES, today=date.today())

            if not source:
                flash("Please specify the income source.", "danger")
                return render_template("income/form.html", sources=INCOME_SOURCES, today=date.today())

            income_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

            new_income = Income(
                amount=amount,
                source=source,
                date=income_date,
                description=description,
                user_id=current_user.id,
            )
            db.session.add(new_income)
            db.session.commit()

            flash(f"Income of ₹{amount:,.2f} from {source} added successfully!", "success")
            return redirect(url_for("income.index"))

        except ValueError:
            flash("Invalid input values. Please check amount and date format.", "danger")

    return render_template("income/form.html", sources=INCOME_SOURCES, today=date.today(), income=None)


@income_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    income = db.session.get(Income, id)
    if not income:
        abort(404)
    # Ensure user data isolation
    if income.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", 0))
            source = request.form.get("source", "").strip()
            date_str = request.form.get("date", "")
            description = request.form.get("description", "").strip()

            if amount <= 0:
                flash("Amount must be greater than zero.", "danger")
                return render_template("income/form.html", sources=INCOME_SOURCES, income=income)

            if not source:
                flash("Please specify the income source.", "danger")
                return render_template("income/form.html", sources=INCOME_SOURCES, income=income)

            income.amount = amount
            income.source = source
            income.date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else income.date
            income.description = description

            db.session.commit()
            flash("Income record updated successfully!", "success")
            return redirect(url_for("income.index"))

        except ValueError:
            flash("Invalid input values. Please check amount and date format.", "danger")

    return render_template("income/form.html", sources=INCOME_SOURCES, income=income)


@income_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    income = db.session.get(Income, id)
    if not income:
        abort(404)
    # Ensure user data isolation
    if income.user_id != current_user.id:
        abort(403)

    amount = income.amount
    source = income.source
    db.session.delete(income)
    db.session.commit()
    flash(f"Income record (₹{amount:,.2f} - {source}) deleted.", "info")
    return redirect(url_for("income.index"))
