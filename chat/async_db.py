from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ACTION:
    SEND_MESSAGE = 'SEND_MESSAGE'

@database_sync_to_async
def sendMessage(data):
    return {
        'data': data,
        'status': 200,
        'message': 'Send message successfully!'
    }