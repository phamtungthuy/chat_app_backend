from django.db import models
from channel.models import Channel, Member
import datetime

MESSAGE_TYPE = (
    ("TEXT", "text"),
    ("IMAGE", "image")
)

class Message(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE, default="TEXT")
    content = models.TextField(blank=True)
    reply = models.ForeignKey("Message", null=True, blank=True, on_delete=models.DO_NOTHING)
    create_at = models.DateTimeField(auto_now_add=True)
    image = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    reactions = models.TextField(blank=True, default="")
    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.channel.id}_{self.content}'
    
    def save(self, *args, **kwargs):
        channel = Channel.objects.get(pk=self.channel.id)
        channel.last_updated = datetime.datetime.now()
        channel.save()
        super().save(*args, **kwargs)

class Emoji(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    url = models.CharField(max_length=50)

class Reaction(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    emoji = models.ForeignKey(Emoji, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.member)


