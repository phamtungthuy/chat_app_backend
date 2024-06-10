import json

from channels.generic.websocket import AsyncWebsocketConsumer
import traceback
from . import async_db
from .async_db import ACTION, TARGET
from channels.exceptions import StopConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.accept()
            return await self.close(code=3000)
        else:
            self.user = self.scope['user']
        await async_db.setOnlineUser(self.user)
        channels = await async_db.getUserChannels(self.user)
        for channel in channels:
            group_name = f'group_{channel.id}'
            await self.channel_layer.group_add(group_name, self.channel_name)
        await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
        await self.channel_layer.group_add("general", self.channel_name)
        await self.accept()
        
        
    async def disconnect(self, close_code):
        # Leave room group
        if close_code == 3000:
            return
        await async_db.setOfflineUser(self.user)
        raise StopConsumer()
        
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            data = await self.dbAsyncHandle(text_data_json)
            target = text_data_json.get('target', 'user')
            targetId = text_data_json.get('targetId', self.user.id)
            for key in data.keys():
                text_data_json[key] = data[key]
            if target == TARGET.USER:
                await self.channel_layer.group_send(
                    f'user_{targetId}', {"type": "chat.message", "text_data_json": text_data_json}
                )
                
            elif target == TARGET.CHANNEL:
                await self.channel_layer.group_send(
                    f'group_{targetId}', {"type": "chat.message", "text_data_json": text_data_json}
                )
            elif target == TARGET.BOTH:
                await self.channel_layer.group_send(
                    f'user_{targetId}', {"type": "chat.message", "text_data_json": text_data_json}
                )
                await self.channel_layer.group_send(
                    f'user_{self.user.id}', {"type": "chat.message", "text_data_json": text_data_json}
                )

        except Exception as e:
            print(str(e))
            text_data_json["data"] = {}
            text_data_json["message"] = str(e)
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
            return await async_db.sendMessage(self.user, targetId, data)
        if action == ACTION.FRIEND_REQUEST:
            return await async_db.sendFriendRequest(self.user, targetId, data)
        if action == ACTION.FRIEND_ACCEPT:
            return await async_db.friendAccept(self, targetId, data)
        if action == ACTION.FRIEND_DENY:
            return await async_db.friendDeny(self.user, targetId)
        if action == ACTION.CANCEL_FRIEND_REQUEST:
            # return await async_db.
            return await async_db.cancelFriendRequest(self.user, targetId)
        if action == ACTION.DELETE_FRIEND:
            return await async_db.deleteFriend(self.user, targetId)
        if action == ACTION.CREATE_CHANNEL:
            return await async_db.createChannel(self.user, data)
        if action == ACTION.GET_MEMBER_LIST:
            return await async_db.getMemberList(targetId)
        if action == ACTION.ADD_MEMBER:
            return await async_db.addMember(targetId, data)
        if action == ACTION.GET_CHANNEL_LIST:
            return await async_db.getChannelList(self.user)
        if action == ACTION.GET_CHAT_LIST:
            return await async_db.getChatList(self.user)
        if action == ACTION.GET_COMMUNITY_LIST:
            return await async_db.getCommunityList(self.user)
        if action == ACTION.GET_MESSAGE_LIST:
            return await async_db.getMessageList(self.user, targetId)
        if action == ACTION.CHANGE_TITLE:
            return await async_db.changeTitle(targetId, data)
        if action == ACTION.GET_FRIEND_LIST:
            return await async_db.getFriendList(self.user)
        if action == ACTION.GET_PROFILE:
            return await async_db.getSelfProfile(self.user)
        if action == ACTION.UPDATE_EXPO_TOKEN:
            return await async_db.updateExpoToken(self.user, data)
        if action == ACTION.SEND_REACTION:
            return await async_db.sendReaction(data)
        
        creator_actions = [ACTION.DELETE_CHANNEL, ACTION.REMOVE_MEMBER, ACTION.CHANGE_CREATOR]
        if targetId in creator_actions:
            if targetId and (await async_db.isCreator(self.user, targetId)):
                if action == ACTION.DELETE_CHANNEL:
                    return await async_db.deleteChannel(targetId)
                if action == ACTION.REMOVE_MEMBER:
                    return await async_db.removeMember(targetId, data)
                if action == ACTION.CHANGE_CREATOR:
                    return await async_db.changeCreator(self.user, data)
                
            else:
                raise Exception("User is not creator to perform this action")
        return {
            "data": data
        }
    