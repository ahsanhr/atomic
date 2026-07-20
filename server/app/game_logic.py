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
