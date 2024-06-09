from django.shortcuts import render
from django.contrib.auth.models import User
from .serializer import UserSerializer
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, Notification
from .utils import sendVerificationEmail, resendVerificationEmail
# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema
from .schema import *

@extend_schema(tags=['User'])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        admin_actions = []
        authenicate_actions = ["getAllUsers"]
        if self.action in authenicate_actions:
            permission_classes = [IsAuthenticated]
        elif self.action in admin_actions:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    @getAllUsersSchema
    def getAllUsers(self, request):
        users = self.queryset.all()
        serializer = self.serializer_class(users, many=True)
        users = serializer.data
        data = []
        friendList = Friend.objects.filter(friend_with=request.user)
        friendIds = []
        for friend in friendList:
            friendIds.append(friend.user.id)
        print(friendIds)
        for user in users:
            user_object = dict(user)
            if user_object["id"] == request.user.id:
                continue
            user_object["is_friend"] = False
            user_object["friend_request_pending"] = False
            try:
                notification = Notification.objects.get(receiver_id=user_object["id"], status="PENDING")
                if notification:
                    user_object["friend_request_pending"] = True
                else: user_object["friend_request_pending"] = False
            except Exception as e:
                print(str(e))
                user_object["friend_request_pending"] = False
            if user_object["id"] in friendIds:
                user_object["is_friend"] = True
            data.append(user_object) 
        return Response({"message": "Get all users successfully", "data": data})
    
    @loginSchema
    def login(self, request):
        username = request.data.get('username', None)
        email = request.data.get('email', None)
        password = request.data.get('password')
        try:
            if username is not None:
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(email=email)
            if (user.check_password(password)):
                userProfile = UserProfile.objects.get(user=user)
                if user.is_active:
                    if (userProfile.verified):
                        refresh = RefreshToken.for_user(user)
                        token = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token)
                        }
                        return Response({"message": "Login successfully", "data": token})
                    else:
                        return Response({"message": "User has not been verified"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({"message": "User has been banned"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'message': "Password not match"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "Username or email not match"}, status=status.HTTP_404_NOT_FOUND)

    @signUpSchema
    def signup(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            try:
                sendVerificationEmail(user, user.email)
            except Exception as e:
                user.delete()
                return Response({"message": "There are some problems when sending verification code"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Verification code was sent", "data": serializer.data})
        except serializers.ValidationError as e:
            message = ""
            for key, value in serializer.errors.items():
                message += f'{value[0]} ({key})'
                break
            if not message: message = e.args[0]
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @resendVerificationSchema
    def resendVerification(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        try:
            user = User.objects.get(username=username)
            if not resendVerificationEmail(user, email):
                return Response({'message': 'User has been already verified'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Verification code was resent", 'data': data})
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    @verifyEmailSchema
    def verifyEmail(self, request):
        data = request.data
        verification_code = data.get('verification_code', None)
        email = data.get('email', None)
        if not verification_code or not email:
            return Response({'message': 'Verification code and email must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
        if not user:
            return Response({'message': 'User not found'},status=status.HTTP_404_NOT_FOUND)
        userProfile = UserProfile.objects.get(user=user)
        if userProfile.verified:
            return Response({'message': 'User has been already verified'}, status=status.HTTP_400_BAD_REQUEST)
        elif userProfile.verification_code == verification_code:
            userProfile.verified = True
            userProfile.verification_code = None 
            userProfile.save()
            return Response({"message": "User has been verified successfully"})
        return Response({"message": "Verification code not correct"}, status=status.HTTP_400_BAD_REQUEST)
    
    
@extend_schema(tags=['Friend'])
class FriendViewSet(viewsets.ViewSet):
    query_set = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        admin_actions = ['getFriendListOfAUser']
        if self.action in admin_actions:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]
    
    @getFriendListSchema
    def getFriendList(self, request):
        user = request.user
        friendList = user.friends.all()
        serializer = self.serializer_class(friendList, many=True)
        return Response({'message': 'Get friend list successfully', 'data': serializer.data})
