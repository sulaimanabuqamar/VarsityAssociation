# Generated by Django 5.0 on 2024-01-13 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basketball', '0013_alter_game_options_alter_player_player_last_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_last_name',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
    ]