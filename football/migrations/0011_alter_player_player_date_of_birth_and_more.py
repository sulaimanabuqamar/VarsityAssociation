# Generated by Django 5.0 on 2024-01-09 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('football', '0010_alter_player_player_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_email',
            field=models.EmailField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_first_name',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_last_name',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_phone_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
