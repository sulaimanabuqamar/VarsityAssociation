# Generated by Django 5.0 on 2023-12-27 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basketball', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_image',
            field=models.ImageField(blank=True, null=True, upload_to='player_images/'),
        ),
    ]
