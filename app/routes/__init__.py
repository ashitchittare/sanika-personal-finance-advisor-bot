from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.income import income_bp
from app.routes.expense import expense_bp
from app.routes.budget import budget_bp
from app.routes.savings import savings_bp
from app.routes.goals import goals_bp
from app.routes.reports import reports_bp
from app.routes.finbot import finbot_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "income_bp",
    "expense_bp",
    "budget_bp",
    "savings_bp",
    "goals_bp",
    "reports_bp",
    "finbot_bp",
]
