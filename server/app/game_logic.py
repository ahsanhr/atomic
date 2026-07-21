"""
game_logic.py — pure progression and financial-health calculations

This file will contain the core game rules without depending on Flask routes
or directly modifying the database.

Fixed furniture progression:
1. chair
2. desk
3. air mattress
4. rug
5. banner
6. bookshelf
7. lamp
8. plant
9. window
10. real bed

Planned responsibilities:
- define the furniture order
- define quest XP rewards
- award XP
- calculate the user's level
- determine XP needed for the next level
- determine which furniture items are unlocked
- detect when a level-up occurs
- calculate short-term vitality from recent spending
- determine whether a user can roll for a friend
- optionally calculate streak or consistency changes

The functions in this file should accept plain values and return plain values.
They should remain independently unit-testable without Flask or SQLAlchemy.
"""

from datetime import date as _date

# xp needed to reach each level, index 0 = level 1 starts here
XP_THRESHOLDS = [0, 100, 250, 450, 700, 1000, 1350, 1750, 2200, 2700]

# what furniture unlocks at each level, None means something else (friend at 5, nothing at 10)
FURNITURE_UNLOCK = {
    1: "airmattress",
    2: "chair",
    3: "desk",
    4: "lamp",
    5: None,
    6: "bookshelf",
    7: "window",
    8: "plant",
    9: "rug",
    10: None,
}

# all the quests in the game with their xp rewards and whether they auto complete
QUESTS = {
    "check_daily_transactions": {
        "label": "check your daily transactions!",
        "period": "daily",
        "xp": 50,
        "auto": False,
    },
    "view_finance_tip": {
        "label": "look at the daily finance tip!",
        "period": "daily",
        "xp": 20,
        "auto": False,
    },
    "input_savings_goal": {
        "label": "input a savings goal!",
        "period": "weekly",
        "xp": 100,
        "auto": False,
    },
    "login_7_times": {
        "label": "login 7 times this week!",
        "period": "weekly",
        "xp": 150,
        "auto": True,
    },
    "make_coffee_4x": {
        "label": "make your own coffee 4x this week",
        "period": "weekly",
        "xp": 80,
        "auto": False,
    },
}


def calculate_level(xp):
    # figure out which level the user is at based on total xp
    level = 1
    for i, threshold in enumerate(XP_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    return min(level, 10)


def award_xp(current_xp, amount):
    # add xp and check if the user leveled up
    old_level = calculate_level(current_xp or 0)
    new_xp = (current_xp or 0) + amount
    new_level = calculate_level(new_xp)
    return new_xp, new_level, new_level > old_level


def calculate_login_xp(streak):
    # base 10 xp plus 5 per day of streak up to 7
    return 10 + 5 * min(streak, 7)


def get_period_key(period, today):
    # returns a string that uniquely identifies this period for deduplication
    if period == "daily":
        return today.isoformat()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def update_login_streak(current_streak, last_login_date, today):
    # returns (new_streak, event)
    # event tells the caller what happened so they can decide what message to show
    if last_login_date is None:
        return 1, "first_login"

    delta = (today - last_login_date).days

    if delta == 0:
        # already logged in today nothing to do
        return current_streak, "same_day"
    elif delta == 1:
        return current_streak + 1, "continued"
    else:
        # missed at least one day so streak resets
        return 1, "reset"


def streak_notification_content(streak, event):
    # returns (title, message) or None if we dont need to create a notification
    if event == "same_day":
        return None

    if event == "first_login":
        return (
            "Welcome to Atomic!",
            "Your streak starts today. Come back tomorrow to keep it going!",
        )

    if event == "reset":
        return (
            "Streak reset",
            "Looks like you missed a day. No worries your new streak starts now!",
        )

    # continued streaks get a generic message unless its a milestone
    if streak % 30 == 0:
        return (
            f"{streak}-day streak milestone!",
            f"A whole month of check-ins! Keep it up!",
        )
    if streak % 7 == 0:
        return (
            f"{streak}-day streak!",
            f"You've logged in {streak} days in a row. You're on fire!",
        )

    return (
        f"Day {streak} streak",
        "Nice work logging in today. Come back tomorrow to keep the streak going!",
    )
