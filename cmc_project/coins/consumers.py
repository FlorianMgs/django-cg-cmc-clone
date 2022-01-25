from channels.generic.websocket import AsyncWebsocketConsumer
import json


class CoinsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('coins', self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard('coins', self.channel_name)

    async def send_new_data(self, event):
        # 'event' parameter is the message sent by 'get_coins_data' celery function
        # We recover the message

        new_data = event['text']
        # And we cast it
        await self.send(json.dumps(new_data))
