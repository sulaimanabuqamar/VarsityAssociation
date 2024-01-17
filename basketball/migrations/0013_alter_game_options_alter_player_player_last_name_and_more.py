# Generated by Django 5.0 on 2024-01-13 19:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basketball', '0012_alter_genderleaguetype_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'verbose_name': 'Basketball  Game'},
        ),
        migrations.AlterField(
            model_name='player',
            name='player_last_name',
            field=models.CharField(blank=True, default='', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='teamcode',
            name='team_code_expiry_date',
            field=models.DateField(default=datetime.date(2024, 1, 20), help_text='Default is 7 days from now'),
        ),
    ]
