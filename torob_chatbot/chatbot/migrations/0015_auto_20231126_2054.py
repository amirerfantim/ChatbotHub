# Generated by Django 3.2.12 on 2023-11-26 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0014_auto_20231125_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatbot',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='chatbot',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='last_message_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]