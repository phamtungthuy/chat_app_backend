from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user.serializer import NotificationSerializer, FriendSerializer, UserProfileSerializer
from user.models import Notification, User, Friend, UserProfile
from channel.async_db import *
from message.async_db import *
import requests
import json
class ACTION:
    SEND_MESSAGE = 'send_message'
    FRIEND_REQUEST = 'friend_request'
    FRIEND_ACCEPT = 'friend_accept'
    FRIEND_DENY = 'friend_deny'
    CREATE_CHANNEL = 'create_channel'
    DELETE_CHANNEL = 'delete_channel'
    GET_MEMBER_LIST = 'get_member_list'
    JOIN_ALL_CHANNELS = 'join_all_channels'
    REMOVE_MEMBER = 'remove_member'
    ADD_MEMBER = 'add_member'
    GET_CHANNEL_LIST = 'get_channel_list'
    GET_MESSAGE_LIST = 'get_message_list'
    CHANGE_CREATOR = 'change_creator'
    CHANGE_TITLE = 'change_title'
    GET_FRIEND_LIST = 'get_friend_list'
    GET_PROFILE = 'get_profile'
    GET_CHAT_LIST = 'get_chat_list'
    GET_COMMUNITY_LIST = 'get_community_list'
    UPDATE_EXPO_TOKEN = 'update_expo_token'
    SEND_REACTION = 'send_reaction'
    
class TARGET:
    USER = 'user'
    CHANNEL = 'channel'

@database_sync_to_async
def updateExpoToken(user, data):
    userProfile = UserProfile.objects.get(user=user)
    expo_token =  data.get("expo_token", None)
    if expo_token:
        userProfile.expo_token = expo_token
        userProfile.save()
    else:
        raise Exception("Expo token not found!")
@database_sync_to_async
def setOnlineUser(user):
    userProfile = UserProfile.objects.get(user=user)
    userProfile.online = True
    userProfile.save()

@database_sync_to_async
def setOfflineUser(user):
    userProfile = UserProfile.objects.get(user=user)
    userProfile.online = False
    userProfile.save()

@database_sync_to_async
def sendMessage(user, channelId, data):
    data['member'] = Member.objects.get(user=user, channel_id=channelId).id
    data['channel'] = channelId
    member_list = Member.objects.filter(channel_id=channelId)
    for member in member_list:
        profile = member.user.profile
        if profile.expo_token:
            expo_url = "https://exp.host/--/api/v2/push/send"
            expo_headers = {
                "Content-Type": "application/json",
            }
            expo_data = {
                "to": profile.expo_token,
                "title": f"Tin nhắn từ {user.username}",
                "body": data["content"]
            }
            requests.post(expo_url, headers=expo_headers, json=expo_data)

    serializer = MessageSerializer(data=data)
    if (serializer.is_valid(raise_exception=True)):
        serializer.save()
    return {
        'data': serializer.data,
        'status': 200,
        'message': 'Send message successfully!'
    }
    
    
@database_sync_to_async
def sendFriendRequest(user, receiver, data):
    data.update({
        "receiver": receiver,
        "sender": user.id,
        "notification_type": "FRIEND_REQUEST"
    })
    if Notification.objects.filter(
        receiver_id=data['receiver'],
        sender_id=data['sender'],
        notification_type="FRIEND_REQUEST",
        status="PENDING"
    ).exists():
        raise Exception("You have already sent friend request to this user")
    if Friend.objects.filter(
        user=user,
        friend_with=receiver
    ).exists():
        raise Exception("You have already been friend with this user")
    serializers = NotificationSerializer(data=data)
    if (serializers.is_valid(raise_exception=True)):
        serializers.save()
        return {
            "data": serializers.data,
            "status": 200,
            "message": "Send friend request successfully!"
        }
        
@database_sync_to_async
def friendAccept(consumer, receiver, data):
    user = consumer.user
    friend_with = User.objects.get(pk=receiver)
    if Friend.objects.filter(user=user, friend_with=friend_with).exists() \
    or Friend.objects.filter(user=friend_with, friend_with=user).exists():
        raise Exception("You have already been friend")
    
    Friend.objects.create(user=user, friend_with=friend_with)
    Friend.objects.create(user=friend_with, friend_with=user)
    
    for channel in Channel.objects.all():
        members = channel.members.all()
        if members.count() == 2:
            if ((members[0].user == user and members[1].user.id == receiver)
            or (members[1].user == user and members[0].user.id == receiver)):
                if not channel.is_active:
                    channel.is_active = True
                    channel.save()
                    data.update({
                        "receiver": receiver,
                        "sender": user.id,
                        "notification_type": "FRIEND_ACCEPT",
                        "status": "HANDLED"
                    })
                    serializer = NotificationSerializer(data=data)
                    if (serializer.is_valid(raise_exception=True)):
                        serializer.save()
                        return serializer.data
                    
    channel = Channel.objects.create(
        title=f'{user.username} || {friend_with.username}',
        avatar_url=user.profile.avatar_url,
        type="CHAT"
    )
    Member.objects.create(user=user, channel=channel)
    Member.objects.create(user=friend_with, channel=channel)               
    
    requestToAccept = Notification.objects.filter(sender_id=receiver,
        receiver=user,
        notification_type='friend_request',
        status='PENDING'
    ).first()
    if requestToAccept:
        requestToAccept.status = 'HANDLED'
        requestToAccept.save()
    data.update({
        "receiver": receiver,
        "sender": user.id,
        "notification_type": "FRIEND_ACCEPT",
        "status": "HANDLED"
    })
    serializer = NotificationSerializer(data=data)
    if (serializer.is_valid(raise_exception=True)):
        serializer.save()
        return serializer.data
    
@database_sync_to_async
def friendDeny(receiver, senderId):
    requestToDeny = Notification.objects.filter(
        receiver=receiver.id,
        sender_id=senderId,
        status='PENDING',
        notification_type="friend_request"
    ).first()
    print(receiver.id, senderId)
    print(Notification.objects.filter(
        receiver=receiver.id,
        sender_id=senderId,
        status='PENDING',
        notification_type="friend_request"
    ).first())
    if requestToDeny:
        requestToDeny.status = 'HANDLED'
        requestToDeny.save()
        serializer = NotificationSerializer(requestToDeny)
        return {
            "data": serializer.data,
            "status": 200
        }
    else:
        raise Exception("You don't have friend request to deny")
    
@database_sync_to_async
def getAllChannels(user):
    members = user.members.all()
    channels = [member.channel for member in members]
    return channels



@database_sync_to_async
def isCreator(user, channelId):
    member = Member.objects.get(user=user, channel_id=channelId)
    if member.role == "CREATOR":
        return True
    return False

@database_sync_to_async
def getFriendList(user):
    friendList = Friend.objects.filter(user=user)
    serializer = FriendSerializer(friendList, many=True)
    return {
        "message": "Get friend list successfully!",
        "status": 200,
        "data": serializer.data
    }
    
@database_sync_to_async
def getSelfProfile(user):
    userProfile = UserProfile.objects.get(user=user)
    serializer = UserProfileSerializer(userProfile, many=False)
    return {
        "message": "Get self profile successfully!",
        "status": 200,
        "data": serializer.data
    }
    
@database_sync_to_async
def sendReaction(data):
    message = Message.objects.get(id=data["message_id"])
    reactions = message.reactions
    if reactions == "":
        reactions = {}
        reactions["value"] = []
        reactions["total"] = 0
    else: reactions = json.loads(reactions)
    if data["value"] not in reactions["value"]:
        reactions["value"].append(data["value"])
    reactions["total"] += 1
    message.reactions = json.dumps(reactions, ensure_ascii=False)
    data["reactions"] = reactions
    message.save()
    return {
        "message": "Send reaction successfully!",
        "status": 200,
        "data": data
    }