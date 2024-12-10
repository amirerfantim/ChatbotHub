from django.db import migrations
from pgvector.django import VectorExtension, VectorField


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0006_message_search_vector'),
    ]

    operations = [
        VectorExtension(),
        migrations.RemoveField(
            model_name='chatbotcontent',
            name='content',
        ),
        migrations.AddField(
            model_name='chatbotcontent',
            name='embedding',
            field=VectorField(blank=True, dimensions=1536, null=True),
        ),
    ]
