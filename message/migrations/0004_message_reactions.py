# Generated by Django 4.2.4 on 2024-06-02 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0003_alter_message_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='reactions',
            field=models.TextField(blank=True, default=''),
        ),
    ]