# Generated by Django 5.0 on 2023-12-28 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0005_alter_player_player_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_shirt_number',
            field=models.IntegerField(),
        ),
    ]