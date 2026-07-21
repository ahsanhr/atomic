"""Notification helpers — creation and real-time delivery via Socket.IO."""

from datetime import datetime, time, timedelta

from app.models import Notification
from app.socket_events import emit_notification
from server.extensions import db


def maybe_create_overage_notification(db_session, user_id, overage_list, today):
    # creates goal_overage notifications but skips if one already exists for
    # that period this week (weekly) or today (daily) so we dont spam the user
    for item in overage_list:
        period = item["period"]

        if period == "weekly":
            week_start = today - timedelta(days=today.weekday())
            cutoff = datetime.combine(week_start, time.min)
            existing = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.type == "goal_overage",
                Notification.title.contains("Weekly"),
                Notification.created_at >= cutoff,
            ).first()
            title = "Weekly spending goal exceeded"
            message = (
                f"You've spent ${item['spent']:.2f} this week against a "
                f"weekly goal of ${item['goal']:.2f}. "
                f"You're ${item['overage']:.2f} over budget."
            )
        else:
            cutoff = datetime.combine(today, time.min)
            existing = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.type == "goal_overage",
                Notification.title.contains("Daily"),
                Notification.created_at >= cutoff,
            ).first()
            title = "Daily spending goal exceeded"
            message = (
                f"You've spent ${item['spent']:.2f} today against a daily "
                f"goal of ${item['goal']:.2f}. "
                f"You're ${item['overage']:.2f} over your daily limit."
            )

        if existing:
            continue

        notif = Notification(
            user_id=user_id,
            type="goal_overage",
            title=title,
            message=message,
        )
        db_session.add(notif)
        db_session.flush()
        emit_notification(user_id, {
            "id": notif.id,
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "is_read": False,
        })
