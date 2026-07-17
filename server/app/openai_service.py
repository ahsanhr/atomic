"""Generate safe, structured financial goals with OpenAI.

The service is deliberately defensive: a missing API key, an exhausted
account, a malformed model response, or a temporary API failure should not
prevent onboarding from completing.  In those cases ``generate_goals``
returns deterministic, locally calculated defaults.
"""

import json
import math
import os

from flask import Blueprint, jsonify, request
from openai import OpenAI


openai_api = Blueprint("openai_api", __name__)
GOAL_KEYS = ("weekly_spend_goal", "monthly_savings_goal", "daily_tip")
DEFAULT_DAILY_TIP = (
    "Review today's spending before making a purchase, and keep one small "
    "amount aside for your savings goal."
)
CREDIT_FALLBACK_TIP = (
    "OpenAI ran out of credits, so these goals were calculated locally."
)


def _number(value):
    """Return a finite, non-negative number or zero for invalid input."""

    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0
    return value if math.isfinite(value) and value >= 0 else 0.0


def _fallback_goals(income, expenses, savings):
    """Build useful defaults without relying on an external service."""

    monthly_income = _number(income)
    monthly_expenses = _number(expenses)
    current_savings = _number(savings)

    # Reserve at least 10% of income when possible, while never setting a
    # savings goal above the amount left after necessary expenses.
    available = max(0.0, monthly_income - monthly_expenses)
    monthly_savings = min(available, max(0.0, monthly_income * 0.10))
    weekly_spend = max(0.0, (monthly_income - monthly_expenses - monthly_savings) / 4.33)

    # Keep money values JSON-friendly and easy to display in the client.
    return {
        "weekly_spend_goal": round(weekly_spend, 2),
        "monthly_savings_goal": round(monthly_savings, 2),
        "daily_tip": DEFAULT_DAILY_TIP,
    }


def _parse_goals(content):
    """Parse and validate the model's JSON without allowing extra shapes."""

    if not isinstance(content, str):
        return None
    try:
        parsed = json.loads(content)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(parsed, dict) or any(key not in parsed for key in GOAL_KEYS):
        return None

    weekly = parsed["weekly_spend_goal"]
    monthly = parsed["monthly_savings_goal"]
    if isinstance(weekly, bool) or isinstance(monthly, bool):
        return None
    try:
        weekly = float(weekly)
        monthly = float(monthly)
    except (TypeError, ValueError):
        return None
    tip = parsed["daily_tip"]
    if not math.isfinite(weekly) or not math.isfinite(monthly) or weekly < 0 or monthly < 0:
        return None
    if not isinstance(tip, str) or not tip.strip():
        return None

    return {
        "weekly_spend_goal": round(weekly, 2),
        "monthly_savings_goal": round(monthly, 2),
        "daily_tip": tip.strip(),
    }


def _parse_tip(content):
    if not isinstance(content, str):
        return None
    try:
        parsed = json.loads(content)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    tip = parsed.get("daily_tip")
    return tip.strip() if isinstance(tip, str) and tip.strip() else None


def _ran_out_of_credits(error):
    message = str(error).lower()
    return any(
        phrase in message
        for phrase in ("insufficient_quota", "exceeded your current quota", "out of credits")
    )


def generate_goals(income, expenses, savings):
    """Return parsed ``weekly_spend_goal``, ``monthly_savings_goal``, and tip.

    The model is asked for JSON twice at most. Any API or parsing failure,
    including an out-of-credit response, falls back to valid local defaults.
    """

    fallback = _fallback_goals(income, expenses, savings)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback

    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        return fallback

    prompt = (
        "You are helping someone make a calm, realistic first-month budget. "
        "Use these monthly amounts: "
        f"income=${_number(income):.2f}, necessary expenses=${_number(expenses):.2f}, "
        f"and current savings=${_number(savings):.2f}. "
        "Set a weekly spending limit only from money left after necessary "
        "expenses and a modest savings contribution. Set a monthly savings "
        "goal that is achievable, never negative, and never greater than the "
        "money available after expenses. If expenses are greater than income, "
        "use zero for both numeric goals and make the tip supportive rather "
        "than judgmental. Write a short, specific daily tip in plain language. "
        "Return ONLY one JSON object with exactly these keys: "
        "weekly_spend_goal (number), monthly_savings_goal (number), "
        "daily_tip (string). Do not include currency symbols, markdown, or "
        "additional keys."
    )
    request = {
        "model": os.getenv("OPENAI_GOALS_MODEL", "gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a thoughtful, encouraging budgeting coach. "
                    "Be practical and non-judgmental; never shame the user "
                    "or pretend to know details they did not provide."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }

    for _ in range(2):
        try:
            response = client.chat.completions.create(**request)
            goals = _parse_goals(response.choices[0].message.content)
            if goals is not None:
                return goals
        except Exception as error:
            # Includes authentication, rate-limit, and insufficient-credit errors. 
            if _ran_out_of_credits(error):
                fallback["daily_tip"] = CREDIT_FALLBACK_TIP
                return fallback
            continue
    return fallback


def generate_tip(income, expenses, savings):
    """Return one short, encouraging daily finance tip."""

    fallback = DEFAULT_DAILY_TIP
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback

    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        return fallback

    request = {
        "model": os.getenv("OPENAI_GOALS_MODEL", "gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a warm, practical budgeting coach. Give advice "
                    "that sounds human and is easy to digest for a large audience, specific, and easy to do today. "
                    "Never shame the user or mention being an AI."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Give one practical daily finance tip based on these monthly "
                    f"amounts: income=${_number(income):.2f}, "
                    f"necessary expenses=${_number(expenses):.2f}, "
                    f"current savings=${_number(savings):.2f}. Keep it to one "
                    "or two friendly sentences, focused on one small action "
                    "the person can take today. Return ONLY JSON with exactly "
                    "one key: daily_tip (string). Do not include markdown or "
                    "additional keys."
                ),
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }

    for _ in range(2):
        try:
            response = client.chat.completions.create(**request)
            tip = _parse_tip(response.choices[0].message.content)
            if tip is not None:
                return tip
        except Exception as error:
            if _ran_out_of_credits(error):
                return CREDIT_FALLBACK_TIP
    return fallback


def _financial_inputs():
    data = request.get_json(silent=True) or {}
    required = ("income", "expenses", "savings")
    if not all(field in data for field in required):
        return None
    return data


@openai_api.post("/goals")
def api_generate_goals():
    data = _financial_inputs()
    if data is None:
        return jsonify(error="income, expenses, and savings are required"), 400
    return jsonify(generate_goals(data["income"], data["expenses"], data["savings"]))


@openai_api.post("/tip")
def api_generate_tip():
    data = _financial_inputs()
    if data is None:
        return jsonify(error="income, expenses, and savings are required"), 400
    tip = generate_tip(data["income"], data["expenses"], data["savings"])
    return jsonify(daily_tip=tip)
