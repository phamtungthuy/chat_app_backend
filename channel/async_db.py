from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Channel, Member
from .serializer import ChannelSerializer, MemberSerializer

@database_sync_to_async
def createChannel(user, data):
    members = data.get('members')
    members = [member for member in members if member != user.id]
    title = data.get('title')
    if len(members) < 2:
        raise Exception('A channel needs at least three members')
    try:
        channel = Channel.objects.create(title=title)
        Member.objects.create(user=user, channel=channel, role="CREATOR")
        for userId in members:
            Member.objects.create(user_id=userId, channel=channel, role="MEMBER")
        channel_layer = get_channel_layer()
        serializer = ChannelSerializer(channel, many=False)
        
        for userId in members:
            async_to_sync(channel_layer.group_send)(
                f'user_{userId}',
                {
                    "type": "chat.message",
                    "text_data_json": {
                        "actioSn": "create_channel",
                        "target": "channel",
                        "targetId": channel.id,
                        "data": serializer.data
                    }
                }
            )
        return {
            "action": "create_channel",
            "target": "channel",
            "targetId": channel.id,
            "data": serializer.data
        }
    except Exception as e:
        channel.delete()
        raise Exception(str(e))
    
@database_sync_to_async
def deleteChannel(targetId):
    try:
        channel = Channel.objects.get(pk=targetId)
        channel.delete()
        return {
            "message": "Your channel is deleted successfully!",
            "data": {
            },
            "status": 200
        }
    except Channel.DoesNotExist:
        raise Exception("Channel not found!")
    
@database_sync_to_async
def getMemberList(targetId):
    try:
        channel = Channel.objects.get(pk=targetId)
        memberList = channel.members.all()
        serializer = MemberSerializer(memberList, many=True)
        return {
            "message": "Get member list successfully!",
            "data": serializer.data,
            "status": 200
        }
    except Channel.DoesNotExist:
        raise Exception('Channel not found!')
    
@database_sync_to_async
def removeMember(channelId, data):
    try:
        member_id = data.get('memberId')
        member = Member.objects.get(pk=member_id, channel_id=channelId)
        member.delete()
        return {
            "message": "Delete member successfully!",
            "data": {},
            "status": 200
        }
    except Channel.DoesNotExist:
        raise Exception('Channel not found!')
    
@database_sync_to_async
def addMember(channelId, data):
    data['channel'] = channelId
    if (Member.objects.filter(user_id=data['user'], channel=channelId).exists()):
        raise Exception('This user has already been member')
    serializer = MemberSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return {
        "message": "Add member successfully!",
        "data": serializer.data,
        "status": 200
    }

@database_sync_to_async
def getUserChannels(user):
    members = user.members.all()
    channels = [member.channel for member in members]
    return channels

@database_sync_to_async
def getChannelList(user):
    members = user.members.all()
    print([member.id for member in members])
    channelList = [member.channel for member in members]
    serializer = ChannelSerializer(channelList, many=True)
    return {
        "message": "Get channels successfully",
        "data": serializer.data,
        "status": 200
    }
    
@database_sync_to_async
def changeCreator(user, data):
    memberId = data.get('memberId')
    newCreator = Member.objects.get(pk=memberId)
    oldCreator = Member.objects.get(user=user, channel=newCreator.channel)
    oldCreator.role = "MEMBER"
    oldCreator.save()
    newCreator.role = "CREATOR"
    newCreator.save()
    return {
        "message": "Change creator of the channel successfully!",
        "data": data,
        "status": 200
    }
    
@database_sync_to_async
def changeTitle(channelId, data):
    title = data.get('title')
    channel = Channel.objects.get(pk=channelId)
    serializer = ChannelSerializer(channel, data=data, partial=True)
    if serializer.is_valid(raise_exception=True):
        channel = serializer.update_title(title)
    data['title'] = channel.title
    return {
        "message": "Change title successfully",
        "data": data,
        "status": 200
    }