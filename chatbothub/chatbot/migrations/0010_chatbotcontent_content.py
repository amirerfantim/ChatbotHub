# Generated by Django 3.2.12 on 2023-11-20 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0009_chatbotcontent'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbotcontent',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
