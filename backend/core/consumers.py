import json
from channels.generic.websocket import AsyncWebsocketConsumer


class EnergyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        await self.channel_layer.group_add('energy_updates', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('energy_updates', self.channel_name)

    async def energy_update(self, event):
        await self.send(text_data=json.dumps(event['payload']))
