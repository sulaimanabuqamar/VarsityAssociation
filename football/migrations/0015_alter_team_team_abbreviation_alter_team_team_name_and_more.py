# Generated by Django 5.0 on 2024-01-17 09:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0014_alter_player_player_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='team_abbreviation',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='teamcode',
            name='team_code_expiry_date',
            field=models.DateField(default=datetime.date(2024, 1, 24), help_text='Default is 7 days from now'),
        ),
    ]
