from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, Emoji, Reaction
from .serializer import MessageSerializer, EmojiSerializer, ReactionSerializer
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
    
        
