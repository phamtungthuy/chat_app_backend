from rest_framework import serializers
from drf_spectacular.utils import inline_serializer
from .serializer import *

class UserResponseSerializer(UserSerializer):
    fullname = serializers.CharField()
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_url', 'email', 
                  'first_name', 'last_name', 'fullname']

class SuccessSignUpSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = UserResponseSerializer()

class TokenDataSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()

class SuccessUserLoginSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = TokenDataSerializer()

class GeneralMessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class UserLoginSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class VerifyEmailSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=10)
    
class ResendVerificationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
class SuccessResendVerificationCode(serializers.Serializer):
    message =serializers.CharField()
    data = ResendVerificationSerializer()

class ChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField()
    newPassword = serializers.CharField()

class ChangeEmailSerializer(serializers.Serializer):
    newEmail = serializers.EmailField()

class UserWithoutEmailSerializer(UserResponseSerializer):
    fullname = serializers.CharField()
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_url', 
                  'first_name', 'last_name', 'fullname']
        

class SuccessGetFriendListSerializer(serializers.Serializer):
    message = serializers.CharField()
    data = UserWithoutEmailSerializer(many=True)
    
class SuccessGetAllUsersSerializer(serializers.Serializer):
    message =serializers.CharField()
    data = UserResponseSerializer(many=True)
