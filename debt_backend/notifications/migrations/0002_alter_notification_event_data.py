# Generated by Django 4.0 on 2022-05-13 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='event_data',
            field=models.JSONField(default=dict),
        ),
    ]