from datetime import date
from app.extensions import db
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.services.ai_advisor import get_ai_financial_advice, generate_local_fallback_advice


def test_finbot_fallback_advisor_execution(app):
    """Test FinBot generates comprehensive local advice without Gemini API Key"""
    with app.app_context():
        user = User(name="FinBot User", email="finbot.user@example.com")
        user.set_password("SecurePass123")
        db.session.add(user)
        db.session.commit()

        today = date.today()
        db.session.add(Income(amount=60000.0, source="Salary", date=today, user_id=user.id))
        db.session.add(Expense(amount=25000.0, category="Rent", date=today, user_id=user.id))
        db.session.add(Expense(amount=12000.0, category="Food", date=today, user_id=user.id))
        db.session.commit()

        # Call with no API key set
        app.config["GEMINI_API_KEY"] = ""
        advice_res = get_ai_financial_advice(user.id, user_query="What is my biggest expense?")

        assert advice_res is not None
        assert "advice" in advice_res
        assert "Rent" in advice_res["advice"]
        assert "₹" in advice_res["advice"]
        assert advice_res["health_score"] > 0
        assert "Local" in advice_res["mode"]


def test_finbot_api_endpoint(auth_client):
    """Test the FinBot /finbot/api/ask endpoint returns valid JSON"""
    res = auth_client.post("/finbot/api/ask", json={"query": "How can I budget better?"})
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert "advice" in json_data
    assert "mode" in json_data
    assert len(json_data["advice"]) > 10
