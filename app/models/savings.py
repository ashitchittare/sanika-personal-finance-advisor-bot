from datetime import datetime, date, timezone
from app.extensions import db


class Savings(db.Model):
    __tablename__ = "savings"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    notes = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "date": self.date.strftime("%Y-%m-%d"),
            "notes": self.notes or "",
            "user_id": self.user_id,
        }

    def __repr__(self):
        return f"<Savings ₹{self.amount} on {self.date}>"
