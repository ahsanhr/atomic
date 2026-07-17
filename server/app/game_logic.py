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
