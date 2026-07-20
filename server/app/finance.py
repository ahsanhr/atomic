"""Deterministic transaction classification and dashboard calculations."""

from collections import Counter, defaultdict
from datetime import date


def classify_transaction(transaction):
    name = " ".join(
        str(transaction.get(key) or "")
        for key in ("merchant_name", "original_name", "name", "description")
    ).lower()
    plaid = transaction.get("personal_finance_category") or {}
    plaid_primary = plaid.get("primary") or (transaction.get("category") or [None])[0]
    plaid_detailed = plaid.get("detailed")

    if (
        "seo " in name
        or "sponsors for educational opportunity" in name
        or "payroll" in name
        or "direct deposit" in name
        or "salary" in name
        or "wages" in name
    ):
        return "income", "income", 1.0
    if plaid_primary and str(plaid_primary).lower() in {
        "income", "transfer_in", "payroll"
    }:
        return "income", "income", 0.9
    if "refund" in name or "reversal" in name:
        return "refund", "refund", 1.0
    if (
        "transfer" in name
        or "checking to savings" in name
        or "savings to checking" in name
    ):
        return "transfer", "transfer", 1.0
    if "credit card payment" in name or "card payment" in name:
        return "payment", "payment", 1.0
    try:
        if float(transaction.get("amount", 0)) < 0:
            return "income", "income", 0.75
    except (TypeError, ValueError):
        pass
    if "atm withdrawal" in name or "cash withdrawal" in name:
        return "expense", "cash", 0.9
    if plaid_primary and any(
        word in str(plaid_primary).lower() for word in ("transfer", "payment")
    ):
        return "transfer", "transfer", 0.85
    if plaid_primary:
        category = str(plaid_primary).lower().replace("_", " ")
        return "expense", category, 0.8
    if not name.strip():
        return "ignored", "other", 1.0
    return "expense", "other", 0.5


def _saved_classification(transaction):
    classified = classify_transaction({
        "merchant_name": getattr(transaction, "merchant_name", None),
        "original_name": getattr(transaction, "original_name", None),
        "category": [transaction.category] if getattr(transaction, "category", None) else [],
        "amount": getattr(transaction, "amount", 0),
        "personal_finance_category": {
            "primary": getattr(transaction, "plaid_primary_category", None),
            "detailed": getattr(transaction, "plaid_detailed_category", None),
        },
    })[0]
    # Correct an older locally stored fallback when Plaid gives us a clear
    # income, refund, transfer, or payment signal.
    if not getattr(transaction, "flow_type", None) or (
        transaction.flow_type == "expense" and classified != "expense"
    ):
        return classified
    return transaction.flow_type


def calculate_dashboard(transactions, today=None):
    today = today or date.today()
    income = 0.0
    expenses = 0.0
    refunds = 0.0
    categories = defaultdict(float)
    merchants = Counter()
    saved_amount = 0.0
    monthly = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})

    for transaction in transactions:
        flow = _saved_classification(transaction)
        amount = abs(float(transaction.amount or 0))
        if flow == "income":
            income += amount
        elif flow == "expense":
            expenses += amount
            categories[transaction.app_category or transaction.category or "other"] += amount
            merchants[transaction.merchant_name or transaction.original_name or "Unknown"] += amount
        elif flow == "refund":
            refunds += amount
        elif flow == "transfer" and "savings" in (
            transaction.merchant_name or transaction.original_name or ""
        ).lower():
            saved_amount += amount

        if transaction.transaction_date:
            key = transaction.transaction_date.strftime("%Y-%m")
            if flow == "income":
                monthly[key]["income"] += amount
            elif flow == "expense":
                monthly[key]["expenses"] += amount
            elif flow == "refund":
                monthly[key]["expenses"] -= amount

    expenses = max(0.0, expenses - refunds)
    monthly_history = []
    for key in sorted(monthly):
        value = monthly[key]
        value["expenses"] = max(0.0, value["expenses"])
        monthly_history.append({
            "month": key,
            "income": round(value["income"], 2),
            "expenses": round(value["expenses"], 2),
            "net_cash_flow": round(value["income"] - value["expenses"], 2),
        })

    surplus = income - expenses
    recommended = min(max(surplus, 0) * 0.50, income * 0.20)
    latest = sorted(
        transactions,
        key=lambda item: item.transaction_date or date.min,
        reverse=True,
    )[:10]
    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "refunds": round(refunds, 2),
        "net_cash_flow": round(surplus, 2),
        "recommended_savings": round(recommended, 2),
        "savings_progress": round(saved_amount, 2),
        "spending_by_category": [
            {"category": key, "amount": round(value, 2)}
            for key, value in sorted(categories.items(), key=lambda pair: pair[1], reverse=True)
        ],
        "top_merchants": [
            {"merchant": key, "amount": round(value, 2)}
            for key, value in merchants.most_common(10)
        ],
        "recent_transactions": [
            {
                "id": item.plaid_transaction_id,
                "merchant": item.merchant_name or item.original_name,
                "amount": round(float(item.amount or 0), 2),
                "date": item.transaction_date.isoformat() if item.transaction_date else None,
                "flow_type": item.flow_type,
                "category": item.app_category or item.category,
            }
            for item in latest
        ],
        "monthly_history": monthly_history,
    }
