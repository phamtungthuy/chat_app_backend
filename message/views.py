from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Message
from .serializer import MessageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from channel.models import Channel, Member
from storages.backends.s3boto3 import S3Boto3Storage
import uuid
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .schema import *
from drf_spectacular.utils import extend_schema
# Create your views here.

@extend_schema(tags=['Message'])
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    @uploadImageSchema
    def uploadImage(self, request):
        file_list = request.FILES.getlist('file')
        # Check whether file is empty
        if file_list is None or len(file_list) == 0:
            return Response({"message": "Attachment file not found"}, status=status.HTTP_400_BAD_REQUEST)
        for file_obj in file_list:
            # Check type and size
            file_type = file_obj.content_type.split('/')[0]
            if file_type != 'image':
                return Response({"message": "File type not supported"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            elif file_obj.size >= 10**7:
                return Response({"message": "File size is too large"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        # Get channel
        data = request.data
        channelId = data.get('channel')
        try: 
            channel = Channel.objects.get(pk=channelId)
        except Channel.DoesNotExist:
            return Response({"message": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)
        # Upload file to s3
        s3 = S3Boto3Storage()
        data['content'] = ''
        data['image'] = ''
        for file_obj in file_list:
            file_path = f'upload/channel/{channel}/{uuid.uuid4()}'
            s3.save(file_path, file_obj)
            file_url = s3.url(file_path)
            data['image'] += file_url + ' '
        # Save to db as message
        try:
            member = Member.objects.get(channel_id=channelId, user=request.user)
            data['member'] = member.id
            data['message_type'] = "IMAGE"
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                text_data_json = {
                    "action": "send_message",
                    "target": "channel",
                    "targetId": channelId,
                    "data": serializer.data
                }
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(f'group_{channelId}', {
                    "type": "chat.message",
                    "text_data_json": text_data_json
                })
                return Response({"message": "Upload file successfully", "data": serializer.data})
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    