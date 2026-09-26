from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def broadcast_doubt_event(class_group_id, event, data):
    channel_layer = get_channel_layer()
    if channel_layer is None :
        return
    async_to_sync(channel_layer.group_send)(
        f'doubts_class_{class_group_id}',
        {"type" : "doubts.event", "event" : event, "data" : data}
    )
    