# Generated by Django 3.2.12 on 2023-11-23 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0011_message_show_original'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='show_original',
        ),
    ]