# Generated by Django 4.0.3 on 2022-04-03 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_profile_friends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='Friends',
            field=models.IntegerField(default=0),
        ),
    ]
