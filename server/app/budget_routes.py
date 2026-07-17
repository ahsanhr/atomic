"""Simple budget calculation endpoint."""

import math

from flask import Blueprint, jsonify, request


budget_api = Blueprint("budget_api", __name__)

INPUT_FIELDS = (
    "monthly_income",
    "monthly_rent_or_mortgage",
    "monthly_groceries_and_takeout",
    "monthly_essentials",
    "monthly_bills",
    "monthly_insurance",
    "monthly_minimum_debt_payments",
)


def _read_amount(data, field):
    """Read one database value as a non-negative dollar amount."""

    try:
        amount = float(data[field])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"{field} must be a non-negative number")
    if not math.isfinite(amount) or amount < 0:
        raise ValueError(f"{field} must be a non-negative number")
    return amount


def calculate_budget(data):
    """Calculate a simple monthly budget from the submitted financial data."""

    income = _read_amount(data, "monthly_income")
    rent = _read_amount(data, "monthly_rent_or_mortgage")
    groceries = _read_amount(data, "monthly_groceries_and_takeout")
    essentials = _read_amount(data, "monthly_essentials")
    bills = _read_amount(data, "monthly_bills")
    insurance = _read_amount(data, "monthly_insurance")
    debt_payments = _read_amount(data, "monthly_minimum_debt_payments")

    needs = (
        rent
        + groceries
        + essentials
        + bills
        + insurance
        + debt_payments
    )
    remaining = income - needs
    emergency_fund_goal = max(needs, 1000)
    emergency_savings = emergency_fund_goal / 3
    wants_budget = max(
        0,
        remaining - emergency_savings,
    )

    summary = {
        "monthly_income": round(income, 2),
        "total_monthly_needs": round(needs, 2),
        "remaining_after_needs": round(remaining, 2),
        "emergency_fund_goal": round(emergency_fund_goal, 2),
        "monthly_emergency_savings": round(emergency_savings, 2),
        "available_wants_budget": round(wants_budget, 2),
    }

    if wants_budget == 0:
        summary["message"] = (
            "Your essential spending is higher than your available income "
            "after emergency savings. Consider reducing expenses or increasing "
            "income before setting aside money for discretionary spending."
        )
    else:
        summary["message"] = "This is the amount available for discretionary spending each month."

    return summary


@budget_api.post("/budget")
def create_budget():
    data = request.get_json(silent=True) or {}
    missing_fields = [field for field in INPUT_FIELDS if field not in data]
    if missing_fields:
        return jsonify(error="Missing fields", fields=missing_fields), 400

    try:
        budget = calculate_budget(data)
    except ValueError as error:
        return jsonify(error=str(error)), 400

    return jsonify(budget)
