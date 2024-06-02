from rest_framework import serializers
from .models import Message, Emoji, Reaction
import channel.serializer
import json

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        data = super(MessageSerializer, self).to_representation(instance)
        memberSerializer = channel.serializer.MemberSerializer(instance.member, many=False)
        data['member'] = memberSerializer.data
        data['channel'] = channel.serializer.ChannelSerializer(instance.channel, many=False).data
        if data["reply"]:
            reply = data["reply"]
            message = Message.objects.get(pk=reply)
            data["reply"] = {
                "_id": reply,
                "text": message.content
            }
            if message.image:
                data["reply"]["image"] = message.image
            if message.location:
                locationArr = message.location.split(" ")
                data["reply"]["location"] = {
                    "latitude": float(locationArr[0]),
                    "longitude": float(locationArr[1])
                }
        if data["reactions"] != "":
            data["reactions"] = json.loads(data["reactions"])
        return data


class EmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emoji
        fields = '__all__'
        

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'