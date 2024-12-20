# Generated by Django 3.2.12 on 2023-11-20 19:11

from django.db import migrations, models
import django.db.models.deletion
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0008_delete_chatbotcontent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatbotContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('chatbot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.chatbot')),
            ],
        ),
    ]
