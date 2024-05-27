from rest_framework import serializers
from .models import Channel, Member
from user.serializer import UserSerializer
from message.models import Message
class ChannelSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    # last_message = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = '__all__'
    
    def get_member_count(self, obj):
        return obj.members.count()


    def validate_title(self, value):
        value = value.strip()
        if len(value) == 0:
            raise serializers.ValidationError('Title must not be blank')
        return value

    def update_title(self, title):
        self.instance.title = title
        self.instance.save()
        return self.instance

    def to_representation(self, instance):
        data = super(ChannelSerializer, self).to_representation(instance)
        if data["type"] == "CHAT" and self.context:
            username = self.context.get("username", None)
            if username:
                title_list = data["title"].split("||")
                for title in title_list:
                    title = title.strip()
                    if username == title:
                        continue
                    data["title"] = title.strip()
            member = Member.objects.get(channel_id=data["id"], user__username=username)
            data["channel_title"] = [member.user.first_name.strip() + " " + member.user.last_name.strip()]
        if data["type"] == "COMMUNITY":
            data["channel_title"] = []
            memberList = Member.objects.filter(channel_id=data["id"])[:3]
            for member in memberList:
                data["channel_title"].append(member.user.first_name.strip() + " " + member.user.last_name.strip())
                
        last_message = Message.objects.filter(channel_id=data["id"]).order_by("-create_at").first()
        if last_message:
            data["last_message"] = last_message.content
        else: data["last_message"] = ""
        return data
    
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

    def to_representation(self, instance):
        data = super(MemberSerializer, self).to_representation(instance)
        userSerializer = UserSerializer(instance.user, many=False)
        data['user'] = userSerializer.get()
        return data

    def validate_nickname(self, value):
        value = value.strip()
        if len(value) == 0:
            raise serializers.ValidationError('Nickname must not be blank')
        return value
    
    def update_nickname(self, nickname):
        self.instance.nickname = nickname
        self.instance.save()
        return self.instance