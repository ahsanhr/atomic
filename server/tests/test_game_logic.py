"""
test_game_logic.py — unit tests for progression rules

This file will test game_logic.py independently from Flask routes and the
database.

Planned test cases:
- XP is awarded correctly
- a user levels up at the correct threshold
- a level-up unlocks the correct furniture item
- unlocked furniture matches the current level
- vitality changes based on recent spending consistency
- users below level 5 cannot roll for a friend
- users at level 5 or above can roll once
- users with an existing friend cannot roll again

Do not write the tests yet.
"""
