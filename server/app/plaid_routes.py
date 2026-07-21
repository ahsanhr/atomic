"""Authenticated Plaid Sandbox routes."""

import os
import time
from datetime import date

from flask import Blueprint, current_app, jsonify, request

from app.auth import login_required
from app.finance import check_spending_overage, classify_transaction
from app.integrations import (
    PlaidError,
    create_plaid_link_token,
    create_sandbox_public_token,
    exchange_plaid_public_token,
    sync_plaid_transactions,
)
from app.models import PlaidItem, UserGoal, UserTransaction
from app.notification_routes import maybe_create_overage_notification
from server.extensions import db


plaid_api = Blueprint("plaid_api", __name__, url_prefix="/api/plaid")


@plaid_api.post("/link-token")
@login_required
def create_link_token(user_id):
    try:
        result = create_plaid_link_token(user_id)
    except PlaidError as error:
        return jsonify(error=str(error)), 503
    return jsonify(link_token=result["link_token"])


@plaid_api.post("/sandbox-token")
@login_required
def create_sandbox_token(user_id):
    existing_items = PlaidItem.query.filter_by(user_id=user_id).all()
    has_transactions = UserTransaction.query.filter_by(user_id=user_id).first()
    if existing_items and has_transactions:
        return jsonify(already_connected=True)

    if existing_items:
        for item in existing_items:
            db.session.delete(item)
        db.session.commit()

    try:
        result = create_sandbox_public_token()
    except PlaidError as error:
        return jsonify(error=str(error)), 503
    return jsonify(public_token=result["public_token"])


@plaid_api.post("/exchange")
@login_required
def exchange_public_token(user_id):
    body = request.get_json(silent=True) or {}
    public_token = body.get("public_token", "").strip()
    if not public_token:
        return jsonify(error="public_token is required"), 400

    try:
        result = exchange_plaid_public_token(public_token)
    except PlaidError as error:
        return jsonify(error=str(error)), 502

    item_data = result.get("item", {})
    item_id = item_data.get("item_id") or result.get("item_id")
    access_token = result.get("access_token")
    if not item_id or not access_token:
        return jsonify(error="Plaid returned an incomplete Item"), 502

    item = PlaidItem.query.filter_by(item_id=item_id).first()
    if item is None:
        item = PlaidItem(user_id=user_id, item_id=item_id, access_token=access_token)
    else:
        item.user_id = user_id
        item.access_token = access_token

    db.session.add(item)
    db.session.commit()
    return jsonify(item_id=item.item_id), 201


@plaid_api.post("/sync")
@login_required
def sync_transactions(user_id):
    items = PlaidItem.query.filter_by(user_id=user_id).all()
    if not items:
        return jsonify(error="No Plaid account is connected"), 404

    added_count = 0
    modified_count = 0
    removed_count = 0

    try:
        for item in items:
            has_more = True
            while has_more:
                if (
                    not item.sync_cursor
                    and os.getenv("PLAID_ENV", "sandbox").lower() == "sandbox"
                    and not current_app.testing
                ):
                    time.sleep(5)
                result = sync_plaid_transactions(item.access_token, item.sync_cursor)
                for transaction in result.get("added", []):
                    _save_transaction(user_id, transaction)
                    added_count += 1
                for transaction in result.get("modified", []):
                    _save_transaction(user_id, transaction)
                    modified_count += 1
                for transaction in result.get("removed", []):
                    existing = UserTransaction.query.filter_by(
                        plaid_transaction_id=transaction["transaction_id"]
                    ).first()
                    if existing:
                        db.session.delete(existing)
                        removed_count += 1
                item.sync_cursor = result.get("next_cursor")
                has_more = result.get("has_more", False)
        db.session.commit()
    except (PlaidError, KeyError, ValueError) as error:
        db.session.rollback()
        return jsonify(error=str(error)), 502

    # after syncing check if the user went over their spending goals
    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if goal and goal.weekly_spending_goal:
        today = date.today()
        all_txns = UserTransaction.query.filter_by(user_id=user_id).all()
        overages = check_spending_overage(all_txns, goal.weekly_spending_goal, today)
        if overages:
            maybe_create_overage_notification(db.session, user_id, overages, today)
            db.session.commit()

    print(
        f"[plaid sync] added={added_count} modified={modified_count} removed={removed_count}",
        flush=True,
    )
    return jsonify(
        added=added_count,
        modified=modified_count,
        removed=removed_count,
    )


def _save_transaction(user_id, transaction):
    transaction_id = transaction["transaction_id"]
    saved = UserTransaction.query.filter_by(
        plaid_transaction_id=transaction_id
    ).first()
    if saved is None:
        saved = UserTransaction(
            user_id=user_id,
            plaid_transaction_id=transaction_id,
        )

    category_data = transaction.get("personal_finance_category") or {}
    categories = transaction.get("category") or []
    flow_type, app_category, confidence = classify_transaction(transaction)
    saved.amount = transaction.get("amount", 0)
    saved.merchant_name = transaction.get("merchant_name") or transaction.get("name") or transaction.get("description")
    saved.original_name = transaction.get("original_name") or transaction.get("description")
    saved.plaid_primary_category = category_data.get("primary") or (categories[0] if categories else None)
    saved.plaid_detailed_category = category_data.get("detailed")
    saved.category = saved.plaid_primary_category
    saved.pending = bool(transaction.get("pending", False))
    saved.flow_type = flow_type
    saved.app_category = app_category
    saved.classification_confidence = confidence
    saved.transaction_date = _transaction_date(transaction.get("date"))
    db.session.add(saved)


def _transaction_date(value):
    if not value:
        return None
    return date.fromisoformat(value)
