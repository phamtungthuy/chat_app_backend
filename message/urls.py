from django.urls import path
from .views import MessageViewSet
urlpatterns = [
    path('upload/image/', MessageViewSet.as_view({
        'post': 'uploadImage',
    })),
]