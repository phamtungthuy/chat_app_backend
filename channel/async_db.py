from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Channel, Member
from .serializer import ChannelSerializer, MemberSerializer

@database_sync_to_async
def createChannel(user, data):
    members = data.get('members')
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
            "data": {
                "message": "Your channel has been deleted!"
            }
        }
    except Channel.DoesNotExist:
        raise Exception("Channel not found!")
    
@database_sync_to_async
def getMemberList(user, targetId, data):
    try:
        channel = Channel.objects.get(pk=targetId)
        memberList = channel.members.all()
        serializer = MemberSerializer(memberList, many=True)
        return {
            "message": "Get member list successfully!",
            "data": serializer.data
        }
    except Channel.DoesNotExist:
        raise Exception('Channel not found!')
    
@database_sync_to_async
def removeMember(channelId, data):
    try:
        member_id = data.get('member')
        member = Member.objects.get(pk=member_id, channel_id=channelId)
        member.delete()
        return {
            "message": "Delete member successfully!",
            "data": ""
        }
    except Channel.DoesNotExist:
        raise Exception('Channel not found!')