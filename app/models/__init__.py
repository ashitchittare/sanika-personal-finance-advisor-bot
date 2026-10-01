from app.extensions import db, login_manager
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense, EXPENSE_CATEGORIES
from app.models.budget import Budget
from app.models.savings import Savings
from app.models.goal import FinancialGoal


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


__all__ = [
    "User",
    "Income",
    "Expense",
    "EXPENSE_CATEGORIES",
    "Budget",
    "Savings",
    "FinancialGoal",
    "load_user",
]
