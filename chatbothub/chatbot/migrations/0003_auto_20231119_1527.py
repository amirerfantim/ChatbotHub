# Generated by Django 3.2.12 on 2023-11-19 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_remove_customuser_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='is_bot',
        ),
        migrations.AddField(
            model_name='message',
            name='role',
            field=models.TextField(default='user'),
            preserve_default=False,
        ),
    ]
