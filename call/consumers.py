import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'Test-Room'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        print("Disconnected!")
    
    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        
        receive_dict["message"]["receiver_channel"] = self.channel_name
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send.sdp",
                "receive_dict": receive_dict
            }
        )
        
    async def send_sdp(self, event):
        receive_dict = event["receive_dict"]
        
        await self.send(text_data=json.dumps(receive_dict))