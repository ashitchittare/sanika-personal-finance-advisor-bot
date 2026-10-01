from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.goal import FinancialGoal

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")


@goals_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    today = date.today()
    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()
            target_amount = float(request.form.get("target_amount", 0))
            current_amount = float(request.form.get("current_amount", 0))
            target_date_str = request.form.get("target_date", "")

            if not title:
                flash("Goal title is required.", "danger")
                return redirect(url_for("goals.index"))

            if target_amount <= 0:
                flash("Target amount must be greater than zero.", "danger")
                return redirect(url_for("goals.index"))

            if current_amount < 0:
                flash("Current saved amount cannot be negative.", "danger")
                return redirect(url_for("goals.index"))

            if not target_date_str:
                flash("Please specify a target completion date.", "danger")
                return redirect(url_for("goals.index"))

            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()

            new_goal = FinancialGoal(
                title=title,
                target_amount=target_amount,
                current_amount=current_amount,
                target_date=target_date,
                user_id=current_user.id
            )
            db.session.add(new_goal)
            db.session.commit()

            flash(f"Goal '{title}' created successfully!", "success")
            return redirect(url_for("goals.index"))

        except ValueError:
            flash("Invalid input values. Please check amount and date format.", "danger")
            return redirect(url_for("goals.index"))

    goals = FinancialGoal.query.filter_by(user_id=current_user.id).order_by(FinancialGoal.target_date.asc()).all()
    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_progress = round((total_saved / total_target * 100), 1) if total_target > 0 else 0

    return render_template(
        "goals/index.html",
        goals=goals,
        total_target=total_target,
        total_saved=total_saved,
        overall_progress=overall_progress,
        today=today,
    )


@goals_bp.route("/update-progress/<int:id>", methods=["POST"])
@login_required
def update_progress(id):
    goal = db.session.get(FinancialGoal, id)
    if not goal:
        abort(404)
    if goal.user_id != current_user.id:
        abort(403)

    try:
        add_amount = float(request.form.get("add_amount", 0))
        if add_amount <= 0:
            flash("Please enter a positive amount to add to your goal.", "warning")
            return redirect(url_for("goals.index"))

        goal.current_amount += add_amount
        db.session.commit()

        if goal.is_completed:
            flash(f"🎉 Congratulations! You have achieved your goal: '{goal.title}'!", "success")
        else:
            flash(f"Added ₹{add_amount:,.2f} to '{goal.title}'. Current progress: {goal.progress_percentage}%", "success")

    except ValueError:
        flash("Invalid amount entered.", "danger")

    return redirect(url_for("goals.index"))


@goals_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    goal = db.session.get(FinancialGoal, id)
    if not goal:
        abort(404)
    if goal.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()
            target_amount = float(request.form.get("target_amount", 0))
            current_amount = float(request.form.get("current_amount", 0))
            target_date_str = request.form.get("target_date", "")

            if not title or target_amount <= 0:
                flash("Please provide valid title and target amount.", "danger")
                return render_template("goals/edit.html", goal=goal)

            goal.title = title
            goal.target_amount = target_amount
            goal.current_amount = current_amount
            if target_date_str:
                goal.target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()

            db.session.commit()
            flash("Financial goal updated successfully!", "success")
            return redirect(url_for("goals.index"))

        except ValueError:
            flash("Invalid input data.", "danger")

    return render_template("goals/edit.html", goal=goal)


@goals_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    goal = db.session.get(FinancialGoal, id)
    if not goal:
        abort(404)
    if goal.user_id != current_user.id:
        abort(403)

    title = goal.title
    db.session.delete(goal)
    db.session.commit()
    flash(f"Goal '{title}' deleted.", "info")
    return redirect(url_for("goals.index"))
