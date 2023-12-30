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
                ('draws', models.IntegerField(blank=True, null=True)),
                ('points', models.IntegerField(blank=True, null=True)),
                ('goals_for', models.IntegerField(blank=True, null=True)),
                ('goals_against', models.IntegerField(blank=True, null=True)),
                ('goals_difference', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Football Team',
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
                'verbose_name': 'Football Team Code',
            },
        ),
        migrations.CreateModel(
            name='ScoreKeeper',
            fields=[
                ('keeper_id', models.AutoField(primary_key=True, serialize=False)),
                ('keeper_number', models.BigIntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='footable_keeper_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Football Score Keeper',
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
                ('goals', models.IntegerField(blank=True, null=True)),
                ('own_goals', models.IntegerField(blank=True, null=True)),
                ('assists', models.IntegerField(blank=True, null=True)),
                ('shots_on_goal', models.IntegerField(blank=True, null=True)),
                ('tackles', models.IntegerField(blank=True, null=True)),
                ('crosses', models.IntegerField(blank=True, null=True)),
                ('saves', models.IntegerField(blank=True, null=True)),
                ('penalty_kicks', models.IntegerField(blank=True, null=True)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_player_team', to='football.team')),
            ],
            options={
                'verbose_name': 'Football Player',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_id', models.AutoField(primary_key=True, serialize=False)),
                ('game_location', models.CharField(max_length=255, null=True)),
                ('game_time', models.TimeField(blank=True, null=True)),
                ('game_status', models.CharField(choices=[('Soon', 'Soon'), ('First Half', 'First Half'), ('Half Time', 'Half Time'), ('Second Half', 'Second Half'), ('Final', 'Final')], default='Soon', max_length=20)),
                ('game_date', models.DateField()),
                ('team_1_score', models.IntegerField(blank=True, null=True)),
                ('team_2_score', models.IntegerField(blank=True, null=True)),
                ('team_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_team_1_games', to='football.team')),
                ('team_1_draw', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='football_team_1_draw', to='football.team')),
                ('team_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_team_2_games', to='football.team')),
                ('team_2_draw', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='football_team_2_draw', to='football.team')),
                ('team_lost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='football_team_lost', to='football.team')),
                ('team_won', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='football_team_won', to='football.team')),
            ],
            options={
                'verbose_name': 'Football Game',
            },
        ),
        migrations.CreateModel(
            name='PlayerPerformance',
            fields=[
                ('performance_id', models.AutoField(primary_key=True, serialize=False)),
                ('goals', models.IntegerField(blank=True, null=True)),
                ('own_goals', models.IntegerField(blank=True, null=True)),
                ('assists', models.IntegerField(blank=True, null=True)),
                ('shots_on_goal', models.IntegerField(blank=True, null=True)),
                ('tackles', models.IntegerField(blank=True, null=True)),
                ('crosses', models.IntegerField(blank=True, null=True)),
                ('saves', models.IntegerField(blank=True, null=True)),
                ('penalty_kicks', models.IntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_playerperformance_set', to='football.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_playerperformance_set', to='football.player')),
            ],
            options={
                'verbose_name': 'Football Player Performance',
                'unique_together': {('game', 'player')},
            },
        ),
        migrations.CreateModel(
            name='ScoreKeeperGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_game', to='football.game')),
                ('score_keeper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='football_scorekeeper', to='football.scorekeeper')),
            ],
            options={
                'verbose_name': 'Football Score Keeper Game',
                'unique_together': {('game', 'score_keeper')},
            },
        ),
    ]
