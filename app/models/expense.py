from datetime import datetime, date, timezone
from app.extensions import db

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Rent",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Bills",
    "Other",
]


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date.strftime("%Y-%m-%d"),
            "description": self.description or "",
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Expense {self.category} - ₹{self.amount}>"
