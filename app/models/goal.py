from datetime import datetime, date, timezone
from app.extensions import db


class FinancialGoal(db.Model):
    __tablename__ = "financial_goals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.0)
    target_date = db.Column(db.Date, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def progress_percentage(self) -> float:
        if self.target_amount <= 0:
            return 100.0
        pct = (self.current_amount / self.target_amount) * 100.0
        return min(round(pct, 1), 100.0)

    @property
    def remaining_amount(self) -> float:
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def is_completed(self) -> bool:
        return self.current_amount >= self.target_amount

    @property
    def days_remaining(self) -> int:
        delta = (self.target_date - date.today()).days
        return delta

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "remaining_amount": self.remaining_amount,
            "progress_percentage": self.progress_percentage,
            "target_date": self.target_date.strftime("%Y-%m-%d"),
            "days_remaining": self.days_remaining,
            "is_completed": self.is_completed,
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<FinancialGoal {self.title}: ₹{self.current_amount}/₹{self.target_amount}>"
