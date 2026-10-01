from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.ai_advisor import get_ai_financial_advice
from app.services.finance_analytics import get_user_overview, get_financial_health_score

finbot_bp = Blueprint("finbot", __name__, url_prefix="/finbot")


@finbot_bp.route("/")
@login_required
def index():
    overview = get_user_overview(current_user.id)
    health = get_financial_health_score(current_user.id)
    # Generate initial personalized assessment
    initial_advice = get_ai_financial_advice(current_user.id)

    return render_template(
        "finbot/index.html",
        overview=overview,
        health=health,
        initial_advice=initial_advice,
    )


@finbot_bp.route("/api/ask", methods=["POST"])
@login_required
def ask():
    data = request.get_json(silent=True) or {}
    user_query = data.get("query", "").strip()

    advice_result = get_ai_financial_advice(current_user.id, user_query=user_query)
    return jsonify({
        "success": True,
        "advice": advice_result.get("advice", ""),
        "mode": advice_result.get("mode", ""),
        "health_score": advice_result.get("health_score", 0),
        "health_rating": advice_result.get("health_rating", ""),
    })
