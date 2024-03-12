import json

from channels.generic.websocket import AsyncWebsocketConsumer
import traceback
from . import async_db
from .async_db import ACTION

class ChatConsumer(AsyncWebsocketConsumer):
    chat_list = []
    async def connect(self):
        if self.scope["user"].is_anonymous:
            return await self.close(code=3000)
        else:
            self.user = self.scope['user']
        await self.channel_layer.group_add("general", self.channel_name)
        await self.accept()
        
        
    async def disconnect(self, close_code):
        # Leave room group
        for chat_id in self.chat_list:
            await self.channel_layer.group_discard(chat_id, self.channel_name)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            data = await self.dbAsyncHandle(text_data_json)
            for key in data.keys():
                text_data_json[key] = data[key]
            await self.channel_layer.group_send(
                    "general", {"type": "chat.message", "text_data_json": text_data_json}
                )
        except Exception as e:
            traceback.print_exc()
            text_data_json["data"] = {}
            text_data_json["message"] = repr(e)
            text_data_json["status"] = 400
            text_data = json.dumps(text_data_json, ensure_ascii=False)
            await self.send(text_data=text_data)
    
    async def chat_message(self, event):
        text_data_json = event["text_data_json"]
        text_data = json.dumps(text_data_json, ensure_ascii=False)
        # Send message to WebSocket
        await self.send(text_data=text_data)
        
    async def dbAsyncHandle(self, text_data_json):
        action = text_data_json.get('action', None)
        targetId = text_data_json.get('targetId', None)
        data = text_data_json.get('data', {})
        
        if action == ACTION.SEND_MESSAGE:
            return await async_db.sendMessage(data)
        
        return data