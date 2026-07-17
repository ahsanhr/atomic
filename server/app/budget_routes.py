"""Simple budget calculation endpoint."""

import math

from flask import Blueprint, jsonify, request

from server.extensions import db
from app.models import UserFinanceMetrics


budget_api = Blueprint("budget_api", __name__)

INPUT_FIELDS = (
    "user_id",
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


def _read_user_id(data):
    try:
        user_id = int(data["user_id"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("user_id must be a positive integer")
    if user_id < 1:
        raise ValueError("user_id must be a positive integer")
    return user_id


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
        user_id = _read_user_id(data)
        budget = calculate_budget(data)
    except ValueError as error:
        return jsonify(error=str(error)), 400

    metrics = UserFinanceMetrics.query.filter_by(user_id=user_id).first()
    if metrics is None:
        metrics = UserFinanceMetrics(user_id=user_id)

    metrics.rent_or_mortgage = _read_amount(data, "monthly_rent_or_mortgage")
    metrics.takeout_and_groceries = _read_amount(data, "monthly_groceries_and_takeout")
    metrics.essentials = _read_amount(data, "monthly_essentials")
    metrics.bills = _read_amount(data, "monthly_bills")
    metrics.insurance = _read_amount(data, "monthly_insurance")
    metrics.min_debt_payments = _read_amount(data, "monthly_minimum_debt_payments")
    metrics.monthly_take_home_income = _read_amount(data, "monthly_income")
    metrics.total_monthly_needs = budget["total_monthly_needs"]
    metrics.remaining_after_needs = budget["remaining_after_needs"]
    metrics.emergency_fund_goal = budget["emergency_fund_goal"]
    metrics.monthly_emergency_savings = budget["monthly_emergency_savings"]
    metrics.available_wants_budget = budget["available_wants_budget"]
    metrics.budget_message = budget["message"]

    try:
        db.session.add(metrics)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Budget calculated but could not be saved"), 500

    budget["user_id"] = user_id
    return jsonify(budget), 201
