# Generated by Django 5.0 on 2023-12-27 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basketball', '0002_alter_player_player_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_image',
            field=models.ImageField(blank=True, default='/media/images/person-placeholder.png', null=True, upload_to='player_images/'),
        ),
    ]
