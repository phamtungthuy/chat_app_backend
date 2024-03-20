from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user.serializer import NotificationSerializer
from user.models import Notification, User, Friend

class ACTION:
    SEND_MESSAGE = 'SEND_MESSAGE'
    FRIEND_REQUEST = 'friend_request'
    FRIEND_ACCEPT = 'friend_accept'
    FRIEND_DENY = 'friend_deny'
    
class TARGET:
    USER = 'user'
    CHANNEL = 'channel'
    
@database_sync_to_async
def sendMessage(data):
    return {
        'data': data,
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