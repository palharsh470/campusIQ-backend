
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

logger = logging.getLogger(__name__)

def notify(user, kind, message):
    notification = Notification.objects.create(recipient=user, kind=kind, message=message)

    try:
        async_to_sync(get_channel_layer().group_send)(
            f"user_{user.id}",
            {
                "type": "notification_event",
                "event": "notification",
                "data": {
                    "id": notification.id,
                    "kind": notification.kind,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )
    except Exception:
        logger.exception("Live push failed for notification %s", notification.id)

    return notification