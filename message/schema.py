from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers
from .serializer import MessageSerializer, ReactionSerializer, EmojiSerializer
from .schemaSerializer import *

uploadImageSchema = extend_schema(
    summary= "Upload image in conversation",
    description = "You need to provided access token to make this action",
    request=UploadImageMessageRequestSerializer
)

