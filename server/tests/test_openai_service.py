import json

from app import openai_service


def test_generate_goals_handles_varied_inputs_without_crashing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    inputs = [
        (3000, 1800, 500),
        (0, 0, 0),
        (1200, 1500, 20),
        (100000, 25000, 40000),
        ("5000", "2200", "100"),
        (None, "not-a-number", -10),
        (float("inf"), 100, 50),
        (2750.55, 1999.99, 0),
        (800, 400, 1200),
        (4500, 4500, 750),
    ]

    for income, expenses, savings in inputs:
        result = openai_service.generate_goals(income, expenses, savings)
        assert set(result) == {
            "weekly_spend_goal",
            "monthly_savings_goal",
            "daily_tip",
        }
        assert json.loads(json.dumps(result)) == result


def test_generate_goals_falls_back_on_malformed_model_response(monkeypatch):
    class Completions:
        def create(self, **kwargs):
            return {"choices": [{"message": {"content": "not json"}}]}

    class Client:
        chat = type("Chat", (), {"completions": Completions()})()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai_service, "OpenAI", lambda api_key: Client())
    result = openai_service.generate_goals(3000, 1800, 500)
    assert set(result) == set(openai_service.GOAL_KEYS)
    assert result["weekly_spend_goal"] >= 0
