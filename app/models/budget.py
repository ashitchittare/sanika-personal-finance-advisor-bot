from datetime import datetime, timezone
from app.extensions import db


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    monthly_budget = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1 to 12
    year = db.Column(db.Integer, nullable=False)   # e.g., 2026
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Unique constraint per user, category, month, and year
    __table_args__ = (
        db.UniqueConstraint("user_id", "category", "month", "year", name="uq_user_category_month_year"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "monthly_budget": self.monthly_budget,
            "month": self.month,
            "year": self.year,
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Budget {self.category} ({self.month}/{self.year}) - ₹{self.monthly_budget}>"
