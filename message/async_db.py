from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, Emoji, Reaction
from .serializer import MessageSerializer, EmojiSerializer, ReactionSerializer
from channel.serializer import ChannelSerializer
from channel.models import Channel, Member
@database_sync_to_async
def send_message(user, targetId, data):
    try:
        message = Message.objects.create(channel_id=targetId, member__user = user, **data)
        serializer = MessageSerializer(message, many=False)
        return {
            "message": "Create message successfully!",
            "data": serializer.data
        }
    except Exception as e:
        message.delete()
        raise Exception(str(e))
    
        
@database_sync_to_async
def getMessageList(user, targetId):
    try:
        channel = Channel.objects.get(pk=targetId)
        messageList = Message.objects.filter(member__user=user, channel=channel)
        serializer = MessageSerializer(messageList, many=True)
        return {
            "message": "Get all messages successfully!",
            "data": serializer.data
        }
    except Exception as e:
        raise Exception(str(e))
        