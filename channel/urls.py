from django.urls import path
from .views import ChannelViewSet

urlpatterns = [
    path('<int:channelId>/media/', ChannelViewSet.as_view({
        'get': 'getMediaList'
    }))    
]