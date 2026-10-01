import os
from pathlib import Path
from flask import Flask
from app.config import config_by_name, BASE_DIR, INSTANCE_DIR
from app.extensions import db, login_manager


def create_app(config_name: str = None) -> Flask:
    """
    Application Factory Pattern for Personal Finance Advisor Bot.
    Guarantees automatic directory and database initialization on fresh systems.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        instance_path=str(INSTANCE_DIR),
        instance_relative_config=True,
    )

    # 1. Load Configuration
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # 2. Ensure instance/database directory exists physically before DB operations
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception as e:
        app.logger.warning(f"Failed to create instance directory: {e}")

    # 3. Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # 4. Register Jinja Helper Filters
    @app.template_filter("inr")
    def format_inr(value):
        try:
            val = float(value)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @app.context_processor
    def inject_global_variables():
        return {
            "currency_symbol": "₹",
            "app_name": "Personal Finance Advisor Bot",
        }

    # 5. Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.income import income_bp
    from app.routes.expense import expense_bp
    from app.routes.budget import budget_bp
    from app.routes.savings import savings_bp
    from app.routes.goals import goals_bp
    from app.routes.reports import reports_bp
    from app.routes.finbot import finbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(finbot_bp)

    # 6. Initialize Database Tables safely inside Application Context
    with app.app_context():
        from app import models  # Ensure models are imported for metadata registration
        db.create_all()

    return app
