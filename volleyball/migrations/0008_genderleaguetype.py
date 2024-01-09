# Generated by Django 5.0 on 2024-01-06 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volleyball', '0007_alter_teamcode_team_code_expiry_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenderLeagueType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('gender', models.CharField(choices=[('Men', 'Men'), ('Women', 'Women')], default='Men', max_length=20)),
            ],
            options={
                'unique_together': {('gender',)},
            },
        ),
    ]