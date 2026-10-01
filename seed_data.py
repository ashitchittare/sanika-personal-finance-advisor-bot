import os
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.budget import Budget
from app.models.savings import Savings
from app.models.goal import FinancialGoal


def seed_database():
    app = create_app()
    with app.app_context():
        print("[*] Initializing database and creating tables...")
        db.create_all()

        today = date.today()
        current_month = today.month
        current_year = today.year

        # 1. Create or get Demo User
        demo_user = User.query.filter_by(email="demo@finbot.com").first()
        if not demo_user:
            demo_user = User(name="Sanika Joshi", email="demo@finbot.com")
            demo_user.set_password("Demo@1234")
            db.session.add(demo_user)
            db.session.commit()
            print("[+] Created demo user: demo@finbot.com (Password: Demo@1234)")
        else:
            print("[i] Demo user demo@finbot.com already exists.")

        # 2. Create Student Demo User for isolation testing
        student_user = User.query.filter_by(email="student@finbot.com").first()
        if not student_user:
            student_user = User(name="Aarav Sharma", email="student@finbot.com")
            student_user.set_password("Student@1234")
            db.session.add(student_user)
            db.session.commit()
            print("[+] Created student user: student@finbot.com (Password: Student@1234)")
        else:
            print("[i] Student user student@finbot.com already exists.")

        # 3. Seed Financial Data for Demo User if not present
        if Income.query.filter_by(user_id=demo_user.id).count() == 0:
            print("[*] Seeding demo financial transactions for Sanika...")

            # Incomes across recent 3 months
            incomes_data = [
                # Current month
                {"amount": 75000.0, "source": "Salary", "date": today.replace(day=1), "desc": "Monthly tech salary"},
                {"amount": 18000.0, "source": "Freelance", "date": today.replace(day=12), "desc": "Web development client gig"},
                {"amount": 4500.0, "source": "Investments", "date": today.replace(day=18), "desc": "Mutual fund dividend yield"},
                # Last month
                {"amount": 75000.0, "source": "Salary", "date": (today.replace(day=1) - timedelta(days=20)).replace(day=1), "desc": "Monthly salary"},
                {"amount": 12000.0, "source": "Freelance", "date": (today.replace(day=1) - timedelta(days=20)).replace(day=15), "desc": "UI design contract"},
                # 2 months ago
                {"amount": 75000.0, "source": "Salary", "date": (today.replace(day=1) - timedelta(days=50)).replace(day=1), "desc": "Monthly salary"},
            ]
            for inc in incomes_data:
                db.session.add(Income(
                    amount=inc["amount"],
                    source=inc["source"],
                    date=inc["date"],
                    description=inc["desc"],
                    user_id=demo_user.id,
                ))

            # Current Month Expenses
            expenses_data = [
                {"amount": 22000.0, "category": "Rent", "date": today.replace(day=2), "desc": "Apartment monthly rent"},
                {"amount": 8500.0, "category": "Food", "date": today.replace(day=5), "desc": "Supermarket groceries & veggies"},
                {"amount": 4200.0, "category": "Food", "date": today.replace(day=14), "desc": "Weekend dining & cafes"},
                {"amount": 4800.0, "category": "Bills", "date": today.replace(day=7), "desc": "Electricity, WiFi & water bills"},
                {"amount": 3500.0, "category": "Transport", "date": today.replace(day=10), "desc": "Metro card recharge & fuel"},
                {"amount": 6800.0, "category": "Shopping", "date": today.replace(day=16), "desc": "Festival clothes & electronics (Over budget)"},
                {"amount": 2500.0, "category": "Entertainment", "date": today.replace(day=19), "desc": "Movie tickets & OTT subscriptions"},
                {"amount": 1800.0, "category": "Healthcare", "date": today.replace(day=21), "desc": "Routine health checkup & supplements"},
                {"amount": 1500.0, "category": "Education", "date": today.replace(day=8), "desc": "Cloud certification course fee"},
            ]
            for exp in expenses_data:
                db.session.add(Expense(
                    amount=exp["amount"],
                    category=exp["category"],
                    date=exp["date"],
                    description=exp["desc"],
                    user_id=demo_user.id,
                ))

            # Budgets for Current Month
            budgets_data = [
                {"category": "Rent", "budget": 22000.0},
                {"category": "Food", "budget": 14000.0},
                {"category": "Bills", "budget": 5000.0},
                {"category": "Transport", "budget": 4000.0},
                {"category": "Shopping", "budget": 5000.0},  # Spent 6800 -> demonstrates overspending warning!
                {"category": "Entertainment", "budget": 3500.0},
                {"category": "Healthcare", "budget": 3000.0},
                {"category": "Education", "budget": 2500.0},
                {"category": "Other", "budget": 2000.0},
            ]
            for b in budgets_data:
                db.session.add(Budget(
                    category=b["category"],
                    monthly_budget=b["budget"],
                    month=current_month,
                    year=current_year,
                    user_id=demo_user.id,
                ))

            # Savings Deposits
            savings_data = [
                {"amount": 25000.0, "date": today.replace(day=3), "notes": "Emergency Fund recurring deposit"},
                {"amount": 15000.0, "date": today.replace(day=15), "notes": "Index fund SIP investment"},
                {"amount": 20000.0, "date": (today.replace(day=1) - timedelta(days=20)).replace(day=5), "notes": "Fixed deposit allocation"},
            ]
            for s in savings_data:
                db.session.add(Savings(
                    amount=s["amount"],
                    date=s["date"],
                    notes=s["notes"],
                    user_id=demo_user.id,
                ))

            # Financial Goals
            goals_data = [
                {
                    "title": "Emergency Reserve (6 Months)",
                    "target_amount": 150000.0,
                    "current_amount": 95000.0,
                    "target_date": today + timedelta(days=120),
                },
                {
                    "title": "New M3 MacBook Pro",
                    "target_amount": 125000.0,
                    "current_amount": 80000.0,
                    "target_date": today + timedelta(days=90),
                },
                {
                    "title": "Goa Vacation Trip",
                    "target_amount": 35000.0,
                    "current_amount": 35000.0,  # 100% completed goal
                    "target_date": today + timedelta(days=30),
                },
            ]
            for g in goals_data:
                db.session.add(FinancialGoal(
                    title=g["title"],
                    target_amount=g["target_amount"],
                    current_amount=g["current_amount"],
                    target_date=g["target_date"],
                    user_id=demo_user.id,
                ))

            db.session.commit()
            print("[+] Demo user financial data successfully seeded!")
        else:
            print("[i] Demo financial data already seeded.")

        # Also add a simple income and expense for student user to verify isolation
        if Income.query.filter_by(user_id=student_user.id).count() == 0:
            db.session.add(Income(amount=15000.0, source="Part-time Tutoring", date=today, description="College tutoring", user_id=student_user.id))
            db.session.add(Expense(amount=3000.0, category="Food", date=today, description="Hostel canteen", user_id=student_user.id))
            db.session.commit()
            print("[+] Student isolated data seeded.")

        print("[*] Database seed completed successfully!")


if __name__ == "__main__":
    seed_database()
