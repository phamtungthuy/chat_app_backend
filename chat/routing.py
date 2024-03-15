from django.urls import re_path

from . import consumers
from call.consumers import CallConsumer
websocket_urlpatterns = [
    re_path(r"ws/chat/", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/call/", CallConsumer.as_asgi()),
]