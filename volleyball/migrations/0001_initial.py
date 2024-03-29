# Generated by Django 5.0 on 2023-12-27 12:16

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('team_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(max_length=40)),
                ('team_abbreviation', models.CharField(max_length=4)),
                ('team_logo', models.ImageField(upload_to='team_logos/')),
                ('manager_first_name', models.CharField(max_length=25)),
                ('manager_last_name', models.CharField(max_length=25)),
                ('manager_phone_number', models.IntegerField()),
                ('manager_email', models.EmailField(max_length=254)),
                ('wins', models.IntegerField(blank=True, null=True)),
                ('loses', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Volleyball Team',
            },
        ),
        migrations.CreateModel(
            name='TeamCode',
            fields=[
                ('team_code_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_code', models.CharField(help_text='Code must be in format XXX-XXX. all in capital letters', max_length=7)),
                ('team_code_expiry_date', models.DateField(default=datetime.date(2024, 1, 3), help_text='Default is 7 days from now')),
                ('team_code_used', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Volleyball Team Code',
            },
        ),
        migrations.CreateModel(
            name='ScoreKeeper',
            fields=[
                ('keeper_id', models.AutoField(primary_key=True, serialize=False)),
                ('keeper_number', models.BigIntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_keeper_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Volleyball Score Keeper',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('player_id', models.AutoField(primary_key=True, serialize=False)),
                ('player_first_name', models.CharField(max_length=25)),
                ('player_last_name', models.CharField(max_length=25)),
                ('player_date_of_birth', models.DateField()),
                ('player_phone_number', models.IntegerField()),
                ('player_email', models.EmailField(max_length=25)),
                ('player_image', models.ImageField(upload_to='player_images/')),
                ('player_shirt_number', models.IntegerField(blank=True, null=True)),
                ('attack_attempts', models.IntegerField(blank=True, null=True)),
                ('kills', models.IntegerField(blank=True, null=True)),
                ('errors', models.IntegerField(blank=True, null=True)),
                ('digs', models.IntegerField(blank=True, null=True)),
                ('blocks', models.IntegerField(blank=True, null=True)),
                ('solo_blocks_and_assisted_blocks', models.IntegerField(blank=True, null=True)),
                ('service_aces', models.IntegerField(blank=True, null=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_player_team', to='volleyball.team')),
            ],
            options={
                'verbose_name': 'Volleyball Player',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.AutoField(primary_key=True, serialize=False)),
                ('sets', models.IntegerField(choices=[(1, 1), (3, 3), (5, 5)])),
                ('game_location', models.CharField(max_length=255, null=True)),
                ('game_time', models.TimeField(blank=True, null=True)),
                ('game_status', models.CharField(choices=[('Soon', 'Soon'), ('Set 1', 'Set 1'), ('Set 2', 'Set 2'), ('Set 3', 'Set 3'), ('Set 4', 'Set 4}'), ('Set 5', 'Set 5'), ('Final', 'Final')], default='Soon', max_length=20)),
                ('game_date', models.DateField()),
                ('team_1_score', models.IntegerField(blank=True, null=True)),
                ('team_2_score', models.IntegerField(blank=True, null=True)),
                ('team_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_team_1_games', to='volleyball.team')),
                ('team_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_team_2_games', to='volleyball.team')),
                ('team_lost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_team_lost', to='volleyball.team')),
                ('team_won', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_team_won', to='volleyball.team')),
            ],
            options={
                'verbose_name': 'Volleyball Game',
            },
        ),
        migrations.CreateModel(
            name='VolleyballSet',
            fields=[
                ('set_id', models.AutoField(primary_key=True, serialize=False)),
                ('set_number', models.IntegerField()),
                ('team_1_points', models.IntegerField(blank=True, null=True)),
                ('team_2_points', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_set', to='volleyball.game')),
            ],
            options={
                'verbose_name': 'Volleyball Set',
                'unique_together': {('set_number', 'game')},
            },
        ),
        migrations.CreateModel(
            name='ScoreKeeperGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_game', to='volleyball.game')),
                ('score_keeper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_scorekeeper', to='volleyball.scorekeeper')),
            ],
            options={
                'verbose_name': 'Volleyball Score Keeper Game',
                'unique_together': {('game', 'score_keeper')},
            },
        ),
        migrations.CreateModel(
            name='PlayerPerformance',
            fields=[
                ('performance_id', models.AutoField(primary_key=True, serialize=False)),
                ('attack_attempts', models.IntegerField(blank=True, null=True)),
                ('kills', models.IntegerField(blank=True, null=True)),
                ('errors', models.IntegerField(blank=True, null=True)),
                ('digs', models.IntegerField(blank=True, null=True)),
                ('blocks', models.IntegerField(blank=True, null=True)),
                ('solo_blocks_and_assisted_blocks', models.IntegerField(blank=True, null=True)),
                ('service_aces', models.IntegerField(blank=True, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_playerperformance_set', to='volleyball.player')),
                ('volleyball_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volleyball_playerperformance_set', to='volleyball.volleyballset')),
            ],
            options={
                'verbose_name': 'Volleyball Player Performance',
                'unique_together': {('volleyball_set', 'player')},
            },
        ),
    ]
