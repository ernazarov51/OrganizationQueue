import json

from channels.generic.websocket import AsyncWebsocketConsumer




class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            await self.send(text_data=json.dumps({"username": self.user.username}))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )



    async def send_notification(self, event):
        print(json.dumps(event))
        await self.send(text_data=json.dumps(event["data"]))
