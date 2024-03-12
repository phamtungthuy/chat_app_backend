from django.urls import path
from .views import UserViewSet
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
    }))
]