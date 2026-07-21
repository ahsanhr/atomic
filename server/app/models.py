from datetime import datetime, timezone
from server.extensions import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    goal = db.relationship("UserGoal", backref="user", uselist=False)
    transactions = db.relationship("UserTransaction", backref="user")
    room_state = db.relationship("UserRoomState", backref="user", uselist=False)
    quest_completions = db.relationship("UserQuestCompletion", backref="user")
    finance_metrics = db.relationship("UserFinanceMetrics", backref="user", uselist=False)
    plaid_items = db.relationship("PlaidItem", backref="user")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")


class UserGoal(db.Model):
    __tablename__ = "user_goals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    weekly_spending_goal = db.Column(db.Float)
    monthly_savings_goal = db.Column(db.Float)
    daily_finance_tip = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserTransaction(db.Model):
    __tablename__ = "user_transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    plaid_transaction_id = db.Column(db.String(255), unique=True)
    amount = db.Column(db.Float)
    category = db.Column(db.String(255))
    merchant_name = db.Column(db.String(255))
    original_name = db.Column(db.String(255))
    plaid_primary_category = db.Column(db.String(255))
    plaid_detailed_category = db.Column(db.String(255))
    pending = db.Column(db.Boolean, default=False)
    flow_type = db.Column(db.String(32))
    app_category = db.Column(db.String(255))
    classification_confidence = db.Column(db.Float)
    transaction_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class PlaidItem(db.Model):
    """A user's linked Plaid Sandbox or production account connection."""

    __tablename__ = "plaid_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.String(255), unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    sync_cursor = db.Column(db.Text)
    institution_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class UserRoomState(db.Model):
    __tablename__ = "user_room_states"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    current_level = db.Column(db.Integer, default=1)
    current_xp = db.Column(db.Integer, default=0)
    login_streak = db.Column(db.Integer, default=0)
    last_login_at = db.Column(db.Date, nullable=True)
    vitality_status = db.Column(db.Boolean, default=True)


class UserQuestCompletion(db.Model):
    __tablename__ = "user_quest_completions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quest_key = db.Column(db.String(255))
    quest_period = db.Column(db.String(50))
    quest_period_key = db.Column(db.String(255))
    completion_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserFinanceMetrics(db.Model):
    __tablename__ = "user_finance_metrics"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rent_or_mortgage = db.Column(db.Float)
    takeout_and_groceries = db.Column(db.Float)
    essentials = db.Column(db.Float)
    bills = db.Column(db.Float)
    insurance = db.Column(db.Float)
    min_debt_payments = db.Column(db.Float)
    monthly_take_home_income = db.Column(db.Float)
    total_monthly_needs = db.Column(db.Float)
    remaining_after_needs = db.Column(db.Float)
    emergency_fund_goal = db.Column(db.Float)
    monthly_emergency_savings = db.Column(db.Float)
    available_wants_budget = db.Column(db.Float)
    budget_message = db.Column(db.Text)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
