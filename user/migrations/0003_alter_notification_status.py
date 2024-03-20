# Generated by Django 5.0.3 on 2024-03-18 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_friend_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.CharField(choices=[('PENDING', 'pending'), ('HANDLED', 'handled')], default='PENDING', max_length=10),
        ),
    ]
