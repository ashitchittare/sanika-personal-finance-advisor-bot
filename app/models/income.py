from datetime import datetime, date, timezone
from app.extensions import db


class Income(db.Model):
    __tablename__ = "incomes"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)  # e.g., Salary, Freelance, Investments, Bonus, Business, Other
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "source": self.source,
            "date": self.date.strftime("%Y-%m-%d"),
            "description": self.description or "",
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Income {self.source} - ₹{self.amount}>"
