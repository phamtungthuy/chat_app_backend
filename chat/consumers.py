import json

from channels.generic.websocket import AsyncWebsocketConsumer
import traceback
from . import async_db
from .async_db import ACTION, TARGET

class ChatConsumer(AsyncWebsocketConsumer):
    chat_list = []
    async def connect(self):
        if self.scope["user"].is_anonymous:
            return await self.close(code=3000)
        else:
            self.user = self.scope['user']
        await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
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
            target = text_data_json.get('target', '')
            for key in data.keys():
                text_data_json[key] = data[key]
            if target == TARGET.USER:
                userId = text_data_json['targetId']
                await self.channel_layer.group_send(
                    f'user_{userId}', {"type": "chat.message", "text_data_json": text_data_json}
                )
                
            elif target == TARGET.CHANNEL:
                channelId = text_data_json['targetId']
                await self.channel_layer.group_send(
                    f'group_{channelId}', {"type": "chat.message", "text_data_json": text_data_json}
                )
            else:
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
       
    async def joinAllChannels(self):
        channels = await async_db.getAllChannels(self.user)
        for channel in channels:
            group_name = f'group_{channel.id}'
            await self.channel_layer.group_add(group_name, self.channel_name)
        
     
    async def dbAsyncHandle(self, text_data_json):
        action = text_data_json.get('action', None)
        targetId = text_data_json.get('targetId', None)
        target = text_data_json.get('target', None)
        data = text_data_json.get('data', {})
        
        if action == ACTION.JOIN_ALL_CHANNELS:
            await self.joinAllChannels()
            return {
                "message": "Join all channels successfully!"
            }
        
        if action == ACTION.SEND_MESSAGE:
            return await async_db.sendMessage(data)
        if action == ACTION.FRIEND_REQUEST:
            return await async_db.sendFriendRequest(self.user, targetId, data)
        if action == ACTION.FRIEND_ACCEPT:
            return await async_db.friendAccept(self, targetId, data)
        if action == ACTION.FRIEND_DENY:
            return await async_db.friendDeny(self.user, targetId)
        if action == ACTION.CREATE_CHANNEL:
            return await async_db.createChannel(self.user, data)
        if action == ACTION.GET_MEMBER_LIST:
            return await async_db.getMemberList(self.user, targetId, data)
        
        if (await async_db.isCreator(self.user, targetId)):
            if action == ACTION.DELETE_CHANNEL:
                return await async_db.deleteChannel(targetId)
            if action == ACTION.REMOVE_MEMBER:
                return await async_db.removeMember(targetId, data)
        else:
            raise Exception("User is not creator to perform this action")
        return data
    