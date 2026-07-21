# shared helpers for quest completion used by auth and quest_routes
# keeps the db logic in one place so neither module duplicates it

from datetime import timedelta

from app.game_logic import QUESTS, award_xp, get_period_key
from app.models import UserGoal, UserQuestCompletion, UserTransaction


def _already_completed(session, user_id, quest_key, period_key):
    return (
        session.query(UserQuestCompletion)
        .filter_by(user_id=user_id, quest_key=quest_key, quest_period_key=period_key)
        .first()
        is not None
    )


def complete_quest(session, room_state, user_id, quest_key, today):
    # marks a quest done for this period and awards xp
    # returns (leveled_up, xp_gained) so caller knows what happened
    quest = QUESTS[quest_key]
    period_key = get_period_key(quest["period"], today)

    if _already_completed(session, user_id, quest_key, period_key):
        return False, 0

    session.add(UserQuestCompletion(
        user_id=user_id,
        quest_key=quest_key,
        quest_period=quest["period"],
        quest_period_key=period_key,
    ))

    new_xp, new_level, leveled_up = award_xp(room_state.current_xp or 0, quest["xp"])
    room_state.current_xp = new_xp
    room_state.current_level = new_level
    return leveled_up, quest["xp"]


def track_login_day(session, user_id, today):
    # records a unique login per day so the weekly 7-login quest can count them
    period_key = get_period_key("daily", today)
    if _already_completed(session, user_id, "login_day", period_key):
        return
    session.add(UserQuestCompletion(
        user_id=user_id,
        quest_key="login_day",
        quest_period="daily",
        quest_period_key=period_key,
    ))


def check_spending_quest(session, room_state, user_id, today):
    # auto-complete the transactions quest if today's spending is under the daily limit
    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if not goal or not goal.weekly_spending_goal:
        return
    daily_limit = goal.weekly_spending_goal / 7
    todays_expenses = session.query(UserTransaction).filter(
        UserTransaction.user_id == user_id,
        UserTransaction.transaction_date == today,
        UserTransaction.flow_type == "expense",
    ).all()
    total = sum(abs(t.amount or 0) for t in todays_expenses)
    if total <= daily_limit:
        complete_quest(session, room_state, user_id, "check_daily_transactions", today)


def check_weekly_login_quest(session, room_state, user_id, today):
    # auto-complete the 7-login weekly quest once this week hits 7 login days
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    count = (
        session.query(UserQuestCompletion)
        .filter(
            UserQuestCompletion.user_id == user_id,
            UserQuestCompletion.quest_key == "login_day",
            UserQuestCompletion.quest_period_key >= monday.isoformat(),
            UserQuestCompletion.quest_period_key <= sunday.isoformat(),
        )
        .count()
    )
    if count >= 7:
        complete_quest(session, room_state, user_id, "login_7_times", today)
