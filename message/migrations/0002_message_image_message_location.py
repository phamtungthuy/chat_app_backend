# Generated by Django 4.2.4 on 2024-04-21 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='location',
            field=models.TextField(blank=True, null=True),
        ),
    ]
