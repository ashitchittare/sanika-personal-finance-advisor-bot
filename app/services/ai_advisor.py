import os
import logging
from datetime import date
from flask import current_app
from app.models.goal import FinancialGoal
from app.services.finance_analytics import (
    get_user_overview,
    get_category_breakdown,
    get_budget_vs_actual,
    get_financial_health_score,
)

logger = logging.getLogger(__name__)


def generate_local_fallback_advice(financial_data: dict, user_query: str = "") -> dict:
    """
    Intelligent rule-based financial advisory engine used when Gemini API is unavailable or unconfigured.
    Analyzes real database metrics and generates rich, structured financial insights.
    """
    overview = financial_data["overview"]
    categories = financial_data["categories"]
    budget_data = financial_data["budget"]
    goals = financial_data["goals"]
    health = financial_data["health"]

    income = overview["month_income"] if overview["month_income"] > 0 else overview["total_income"]
    expenses = overview["month_expense"] if overview["month_expense"] > 0 else overview["total_expense"]
    balance = income - expenses
    savings_rate = round((balance / income * 100), 1) if income > 0 else 0.0

    # 1. Spending Analysis
    spending_analysis = []
    if income == 0 and expenses == 0:
        spending_analysis.append("No financial records found for this period. Start by recording your regular monthly income and daily expenses.")
    elif balance < 0:
        spending_analysis.append(f"⚠️ **Budget Deficit Alert:** Your current spending (₹{expenses:,.2f}) exceeds your recorded income (₹{income:,.2f}) by **₹{abs(balance):,.2f}**. Immediate expense cutting is recommended.")
    else:
        spending_analysis.append(f"✅ **Positive Cashflow:** You have a net positive balance of **₹{balance:,.2f}** with a savings rate of **{savings_rate}%**.")

    # 2. High-spending categories
    sorted_cats = sorted([c for c in categories["items"] if c["amount"] > 0], key=lambda x: x["amount"], reverse=True)
    high_spending = []
    if sorted_cats:
        top_cat = sorted_cats[0]
        high_spending.append(f"Your top expense is **{top_cat['category']}** at **₹{top_cat['amount']:,.2f}** ({top_cat['percentage']}% of total spending).")
        if len(sorted_cats) > 1:
            second_cat = sorted_cats[1]
            high_spending.append(f"Second highest expense is **{second_cat['category']}** at **₹{second_cat['amount']:,.2f}** ({second_cat['percentage']}%).")
        if top_cat["percentage"] > 40:
            high_spending.append(f"💡 **Recommendation:** {top_cat['category']} consumes over 40% of your budget. Explore options to optimize or renegotiate these costs.")
    else:
        high_spending.append("No expense categories recorded yet.")

    # 3. Budget Suggestions
    budget_suggestions = []
    overspent_items = [b for b in budget_data["categories"] if b["is_overspent"] and b["has_budget"]]
    if overspent_items:
        for item in overspent_items:
            budget_suggestions.append(f"🚨 **Over Budget in {item['category']}:** Spent ₹{item['spent']:,.2f} against a planned ₹{item['budget']:,.2f} (Over by ₹{abs(item['remaining']):,.2f}).")
    elif budget_data["total_budgeted"] > 0:
        budget_suggestions.append(f"👏 Excellent discipline! All {len(budget_data['categories'])} expense categories are well within their planned limits.")
    else:
        budget_suggestions.append("Set monthly budgets for key categories (like Food, Shopping, Entertainment) to activate automated overspending alerts.")

    # 4. Saving & Goal Suggestions
    saving_suggestions = []
    if income > 0:
        recommended_savings = round(income * 0.20, 2)
        if balance >= recommended_savings:
            saving_suggestions.append(f"Target the **50/30/20 Rule**: You are currently saving ₹{balance:,.2f}, surpassing the recommended minimum 20% savings target of ₹{recommended_savings:,.2f}/month.")
        else:
            saving_suggestions.append(f"Target the **50/30/20 Rule**: Aim to allocate at least 20% (₹{recommended_savings:,.2f}) towards emergency funds and investments each month.")

    if goals:
        active_goals = [g for g in goals if not g["is_completed"]]
        if active_goals:
            for g in active_goals[:2]:
                days = g["days_remaining"]
                remaining_amt = g["remaining_amount"]
                if days > 0:
                    months_left = max(1, round(days / 30))
                    monthly_needed = round(remaining_amt / months_left, 2)
                    saving_suggestions.append(f"🎯 **Goal '{g['title']}':** Needs ₹{remaining_amt:,.2f} in {days} days. Save **₹{monthly_needed:,.2f}/month** to stay on track.")
                else:
                    saving_suggestions.append(f"🎯 **Goal '{g['title']}':** Target date reached. Needs ₹{remaining_amt:,.2f} to complete.")
    else:
        saving_suggestions.append("Create a Financial Goal (e.g. Emergency Fund, Laptop, Vacation) to track your progress with visual milestones.")

    # 5. Personalized Financial Guidance Summary
    personalized_guidance = (
        f"Based on your current Financial Health Score of **{health['score']}/100 ({health['rating']})**, "
        f"your financial posture is {'well-managed and resilient' if health['score'] >= 60 else 'in need of active optimization'}. "
        f"{'Focus on capping discretionary spending (Shopping, Dining, Entertainment) and building an emergency reserve equal to 3-6 months of expenses.' if health['score'] < 60 else 'Continue automating your monthly savings and consider diversifying your surplus into growth assets.'}"
    )

    # Format full text response
    full_markdown = f"""### 📊 FinBot Financial Assessment
**Period:** {overview['month_name']} | **Health Score:** {health['score']}/100 ({health['rating']})

---

#### 1. 💵 Spending & Cashflow Analysis
- {chr(10).join(['- ' + s for s in spending_analysis])}

#### 2. 🔍 High-Spending Breakdown
{chr(10).join(['- ' + h for h in high_spending])}

#### 3. 🎯 Budgeting & Alerts
{chr(10).join(['- ' + b for b in budget_suggestions])}

#### 4. 📈 Savings & Goal Roadmap
{chr(10).join(['- ' + s for s in saving_suggestions])}

---
💡 **FinBot Verdict:**
{personalized_guidance}
"""

    return {
        "advice": full_markdown,
        "mode": "Local Rule-Based Advisor (Zero external latency)",
        "health_score": health["score"],
        "health_rating": health["rating"],
        "spending_analysis": spending_analysis,
        "high_spending": high_spending,
        "budget_suggestions": budget_suggestions,
        "saving_suggestions": saving_suggestions,
        "personalized_guidance": personalized_guidance,
    }


def get_ai_financial_advice(user_id: int, user_query: str = "") -> dict:
    """
    Main entry point for FinBot advice.
    Pulls user metrics from the database, attempts Gemini API inference, and falls back cleanly.
    """
    today = date.today()
    overview = get_user_overview(user_id)
    categories = get_category_breakdown(user_id, today.month, today.year)
    budget = get_budget_vs_actual(user_id, today.month, today.year)
    goals = [g.to_dict() for g in FinancialGoal.query.filter_by(user_id=user_id).all()]
    health = get_financial_health_score(user_id)

    financial_data = {
        "overview": overview,
        "categories": categories,
        "budget": budget,
        "goals": goals,
        "health": health,
    }

    gemini_api_key = current_app.config.get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    gemini_model = current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not gemini_api_key:
        logger.info("GEMINI_API_KEY not set. Using FinBot local rule-based advisor.")
        return generate_local_fallback_advice(financial_data, user_query)

    # If GEMINI_API_KEY is present, attempt Gemini API call
    try:
        # Construct rich financial context prompt
        active_prompt = f"""
You are FinBot, an expert Personal Finance Advisor Bot for an Indian user (currency: INR ₹).
Analyze the user's REAL financial database metrics below and provide clear, actionable, friendly, and structured advice.

USER FINANCIAL DATA:
- Period: {overview['month_name']}
- Monthly Income: ₹{overview['month_income']:,.2f} (All-time total income: ₹{overview['total_income']:,.2f})
- Monthly Expenses: ₹{overview['month_expense']:,.2f} (All-time total expenses: ₹{overview['total_expense']:,.2f})
- Current Month Balance: ₹{overview['month_balance']:,.2f} (Net all-time balance: ₹{overview['net_balance']:,.2f})
- Total Savings Deposited: ₹{overview['current_savings']:,.2f}
- Financial Health Score: {health['score']}/100 ({health['rating']})

EXPENSE BREAKDOWN BY CATEGORY:
{chr(10).join([f"- {item['category']}: ₹{item['amount']:,.2f} ({item['percentage']}%)" for item in categories['items'] if item['amount'] > 0]) or "No expenses recorded this month."}

BUDGET STATUS:
{chr(10).join([f"- {b['category']}: Budgeted ₹{b['budget']:,.2f}, Spent ₹{b['spent']:,.2f}, Remaining ₹{b['remaining']:,.2f} ({'OVER BUDGET' if b['is_overspent'] and b['has_budget'] else 'Within Budget'})" for b in budget['categories'] if b['has_budget'] or b['spent'] > 0]) or "No budgets configured."}

FINANCIAL GOALS:
{chr(10).join([f"- {g['title']}: Target ₹{g['target_amount']:,.2f}, Saved ₹{g['current_amount']:,.2f} ({g['progress_percentage']}%), Target Date: {g['target_date']} ({g['days_remaining']} days remaining)" for g in goals]) or "No goals set."}

USER QUERY / QUESTION:
{user_query if user_query else "Provide a comprehensive financial health review, spending analysis, high-spending warnings, budget optimization suggestions, and saving recommendations."}

RESPONSE GUIDELINES:
1. Use markdown headings, bullet points, and bold text.
2. Always format currency in Indian Rupees with symbol ₹ (e.g. ₹15,000.00).
3. Directly address their high-spending categories and any over-budget items.
4. Provide concrete, realistic advice for Indian cost-of-living and 50/30/20 budget framework.
5. Keep the tone encouraging, analytical, and professional.
"""
        # Use google-genai SDK
        try:
            from google import genai
            client = genai.Client(api_key=gemini_api_key)
            response = client.models.generate_content(
                model=gemini_model,
                contents=active_prompt,
            )
            ai_text = response.text
            return {
                "advice": ai_text,
                "mode": f"Google Gemini AI ({gemini_model})",
                "health_score": health["score"],
                "health_rating": health["rating"],
            }
        except ImportError:
            # Fallback to legacy google.generativeai if installed
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=gemini_api_key)
            model = genai_legacy.GenerativeModel(gemini_model)
            response = model.generate_content(active_prompt)
            return {
                "advice": response.text,
                "mode": f"Google Gemini AI ({gemini_model})",
                "health_score": health["score"],
                "health_rating": health["rating"],
            }
    except Exception as e:
        logger.warning(f"Gemini API request failed: {e}. Falling back to rule-based advisor.")
        fallback_res = generate_local_fallback_advice(financial_data, user_query)
        fallback_res["mode"] = f"Local Fallback Advisor (Gemini API unavailable: {str(e)[:50]}...)"
        return fallback_res
