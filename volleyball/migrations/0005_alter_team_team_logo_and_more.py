# Generated by Django 5.0 on 2023-12-28 08:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volleyball', '0004_alter_player_player_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='team_logo',
            field=models.ImageField(blank=True, default='images/logo-placeholder.png', null=True, upload_to='team_logos/'),
        ),
        migrations.AlterField(
            model_name='teamcode',
            name='team_code_expiry_date',
            field=models.DateField(default=datetime.date(2024, 1, 4), help_text='Default is 7 days from now'),
        ),
    ]
