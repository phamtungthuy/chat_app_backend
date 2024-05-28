from django.urls import path
from .views import UserViewSet, FriendViewSet
from .passwordToken import *

urlpatterns = [
    path('login/', UserViewSet.as_view({
        'post': 'login'
    })),
    path('signup/', UserViewSet.as_view({
        'post': 'signup'
    })),
    path('verify/', UserViewSet.as_view({
        'post': 'verifyEmail'
    })),
    path('verify/resend/', UserViewSet.as_view({
        'post': 'resendVerification'
    })),
    path('passwordreset/', 
        CustomResetPasswordRequestTokenViewSet.as_view({
        'post': 'create'     
    })),
    path('passwordreset/confirm/', 
        CustomResetPasswordConfirmViewSet.as_view({
        'post': 'create'     
    })),
    path('passwordreset/validate/', 
        CustomResetPasswordValidateTokenViewSet.as_view({
        'post': 'create'     
    })),
    path('friends/', FriendViewSet.as_view({
        'get': 'getFriendList',
    })),
    path('all/', UserViewSet.as_view({
        'get': 'getAllUsers',
    })),
]