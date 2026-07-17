"""
models.py — SQLAlchemy database models

This file will contain all database models for the minimal Sprout demo.

Planned models:

User
- account identity and authentication information
- email, password hash, and creation timestamp

Goal
- financial goals generated during onboarding
- weekly spending goal
- monthly savings goal
- rotating daily finance tip
- one active goal record per user

Transaction
- transactions imported from Plaid
- external Plaid transaction ID
- amount, category, and date
- tied to the authenticated user
- external transaction IDs must not be duplicated

RoomState
- long-term game progression
- current level and XP
- login streak
- vitality or mood state
- assigned friend, when unlocked
- one room state per user

QuestCompletion
- records completed daily and weekly quests
- prevents the same quest from awarding XP more than once per period

Friend
- fixed friend characters available through the level-5 roll
- contains the display name and frontend sprite key

Furniture and quest definitions do not need their own database tables.
They will be represented as fixed application constants.
"""
