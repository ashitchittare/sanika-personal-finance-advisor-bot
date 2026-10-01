from app import create_app
from app.models.user import User


def test_full_application_flow():
    """Simulate a complete user lifecycle through the test client"""
    app = create_app("testing")
    client = app.test_client()

    with app.app_context():
        # 1. Register new user
        reg_res = client.post("/auth/register", data={
            "name": "Live Test User",
            "email": "live@test.com",
            "password": "Password123",
            "confirm_password": "Password123"
        }, follow_redirects=True)
        assert reg_res.status_code == 200
        assert b"Financial Dashboard" in reg_res.data

        # 2. Add Income
        inc_res = client.post("/income/add", data={
            "amount": "90000",
            "source": "Salary",
            "date": "2026-10-01",
            "description": "Tech Salary"
        }, follow_redirects=True)
        assert inc_res.status_code == 200
        assert b"90,000.00" in inc_res.data

        # 3. Add Expense
        exp_res = client.post("/expense/add", data={
            "amount": "15000",
            "category": "Food",
            "date": "2026-10-01",
            "description": "Dinner"
        }, follow_redirects=True)
        assert exp_res.status_code == 200
        assert b"15,000.00" in exp_res.data

        # 4. Set Budget
        bud_res = client.post("/budget/", data={
            "category": "Food",
            "monthly_budget": "12000",
            "month": "10",
            "year": "2026"
        }, follow_redirects=True)
        assert bud_res.status_code == 200
        assert b"12,000.00" in bud_res.data

        # 5. Add Savings
        sav_res = client.post("/savings/", data={
            "amount": "20000",
            "date": "2026-10-01",
            "notes": "SIP Mutual Fund"
        }, follow_redirects=True)
        assert sav_res.status_code == 200
        assert b"20,000.00" in sav_res.data

        # 6. Create Goal
        goal_res = client.post("/goals/", data={
            "title": "Emergency Fund",
            "target_amount": "100000",
            "current_amount": "40000",
            "target_date": "2026-12-31"
        }, follow_redirects=True)
        assert goal_res.status_code == 200
        assert b"Emergency Fund" in goal_res.data

        # 7. Check Reports Page and Chart Data API
        rep_res = client.get("/reports/")
        assert rep_res.status_code == 200
        assert b"Financial Reports & Analytics" in rep_res.data

        api_res = client.get("/reports/api/chart-data")
        assert api_res.status_code == 200
        data = api_res.get_json()
        assert "categories" in data
        assert "trends" in data

        # 8. Check FinBot Page and AI Ask API
        fin_page = client.get("/finbot/")
        assert fin_page.status_code == 200
        assert b"FinBot Financial Advisor" in fin_page.data

        ask_res = client.post("/finbot/api/ask", json={"query": "How is my spending in Food?"})
        assert ask_res.status_code == 200
        ask_data = ask_res.get_json()
        assert ask_data["success"] is True
        assert len(ask_data["advice"]) > 20
