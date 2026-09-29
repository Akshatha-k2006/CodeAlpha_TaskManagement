from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def notify(users, message, link="", exclude=None):
    layer = get_channel_layer()
    for u in set(users):
        if u == exclude: continue
        n = Notification.objects.create(recipient=u, message=message, link=link)
        unread = Notification.objects.filter(recipient=u, is_read=False).count()
        async_to_sync(layer.group_send)(f"user_{u.id}", {"type": "push", "message": message, "link": link, "unread": unread, "id": n.id})
