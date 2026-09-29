from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(JsonWebsocketConsumer):
    def connect(self):
        u = self.scope["user"]
        if not u.is_authenticated: return self.close()
        self.group = f"user_{u.id}"
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)
        self.accept()
    def disconnect(self, code):
        if hasattr(self, "group"): async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
    def push(self, event): self.send_json(event)
