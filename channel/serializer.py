from rest_framework import serializers
from .models import Channel, Member
from user.serializer import UserSerializer

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