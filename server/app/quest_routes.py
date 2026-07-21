# quest endpoints — get current quests with completion state, complete manual quests

from datetime import date

from flask import Blueprint, jsonify

from app.auth import login_required
from app.game_logic import FURNITURE_UNLOCK, QUESTS, get_period_key
from app.models import UserQuestCompletion, UserRoomState
from app.quest_helpers import complete_quest
from server.extensions import db

quest_api = Blueprint("quest_api", __name__)


@quest_api.get("")
@login_required
def get_quests(user_id):
    today = date.today()
    daily_key = get_period_key("daily", today)
    weekly_key = get_period_key("weekly", today)

    # grab all completions for today and this week in one query
    completions = UserQuestCompletion.query.filter(
        UserQuestCompletion.user_id == user_id,
        UserQuestCompletion.quest_key.in_(QUESTS.keys()),
        UserQuestCompletion.quest_period_key.in_([daily_key, weekly_key]),
    ).all()
    done_keys = {c.quest_key for c in completions}

    result = []
    for key, q in QUESTS.items():
        result.append({
            "key": key,
            "label": q["label"],
            "period": q["period"],
            "xp": q["xp"],
            "auto": q["auto"],
            "completed": key in done_keys,
        })

    return jsonify(quests=result)


@quest_api.post("/<quest_key>/complete")
@login_required
def complete_quest_route(user_id, quest_key):
    if quest_key not in QUESTS:
        return jsonify(error="unknown quest"), 404

    if QUESTS[quest_key]["auto"]:
        return jsonify(error="this quest completes automatically"), 403

    today = date.today()
    room_state = UserRoomState.query.filter_by(user_id=user_id).first()
    if room_state is None:
        room_state = UserRoomState(user_id=user_id)
        db.session.add(room_state)

    leveled_up, xp_gained = complete_quest(db.session, room_state, user_id, quest_key, today)

    if xp_gained == 0:
        return jsonify(error="already completed this period"), 409

    db.session.commit()

    furniture = FURNITURE_UNLOCK.get(room_state.current_level) if leveled_up else None

    return jsonify(
        xp_gained=xp_gained,
        new_xp=room_state.current_xp,
        new_level=room_state.current_level,
        leveled_up=leveled_up,
        furniture=furniture,
    )
