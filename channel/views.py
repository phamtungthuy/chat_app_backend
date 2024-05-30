from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Channel
from .serializer import ChannelSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from message.serializer import MessageSerializer
from drf_spectacular.utils import extend_schema
# Create your views here.

@extend_schema(tags=['Channel'])
class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    
    def get_permissions(self):
        admin_actions = []
        if self.action in admin_actions:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def getMediaList(self, request, channelId):
        try:
            channel = self.queryset.get(pk=channelId)
            imageList = channel.messages.filter(message_type="IMAGE")
            serializer = MessageSerializer(imageList, many=True)
            mediaList = []
            for obj in serializer.data:
                mediaList.append(obj["image"])
            return Response({"message": "Get media list successfully", "data": mediaList}) 
        except Channel.DoesNotExist:
            return Response({"message": "Channel not found"}, status=status.HTTP_404_NOT_FOUND)