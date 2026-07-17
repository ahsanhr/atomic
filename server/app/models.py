from datetime import datetime, timezone
from server.extensions import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    goal = db.relationship("UserGoal", backref="user", uselist=False)
    transactions = db.relationship("UserTransaction", backref="user")
    room_state = db.relationship("UserRoomState", backref="user", uselist=False)
    quest_completions = db.relationship("UserQuestCompletion", backref="user")
    finance_metrics = db.relationship("UserFinanceMetrics", backref="user", uselist=False)


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
    transaction_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserRoomState(db.Model):
    __tablename__ = "user_room_states"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    current_level = db.Column(db.Integer, default=1)
    current_xp = db.Column(db.Integer, default=0)
    login_streak = db.Column(db.Integer, default=0)
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
