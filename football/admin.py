from django.contrib import admin
from .models import *


class TeamCodeModelAdmin(admin.ModelAdmin):
    list_display = ['team_code',
                    'team_code_expiry_date', 'team_code_used']


class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'team_abbreviation', 'team_logo','team_gender',  'manager_first_name',
                    'manager_last_name', 'manager_phone_number', 'manager_email', 'wins', 'loses']
    search_fields = ['team_name', 'manager_first_name']


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['player_first_name', 'player_last_name', 'player_date_of_birth',
                    'player_phone_number', 'player_email', 'player_image', 'team']
    search_fields = ['player_first_name', 'player_last_name',
                    'player_phone_number', 'player_shirt_number','player_email',  'team']


class ScoreKeeperAdmin(admin.ModelAdmin):
    list_display = ['keeper_id', 'user', 'keeper_number']
    search_fields = ['keeper_id', 'user' 'keeper_number']


class ScoreKeeperGameAdmin(admin.ModelAdmin):
    list_display = ['id', 'score_keeper', 'game', ]
    search_fields = ['score_keeper', 'game']


class GameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'game_location', 'team_1', 'team_2',
                    'game_status', 'game_date', 'team_1_score', 'team_2_score', 'team_won', 'team_lost','team_1_draw','team_2_draw']
    search_fields = ['game_id',
                     'game_location', 'team_1__team_name', 'team_2__team_name']


class PlayerPerformanceAdmin(admin.ModelAdmin):
    list_display = ['performance_id', 'game', 'player', 'goals','own_goals','assists',
                    'shots_on_goal', 'tackles', 'crosses', 'saves', 'penalty_kicks']
    search_fields = ['performance_id', 'game', 'player']

class GenderLeagueTypeAdmin(admin.ModelAdmin):
    list_display = ['gender','image']
    
admin.site.register(GenderLeagueType, GenderLeagueTypeAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(ScoreKeeper, ScoreKeeperAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(PlayerPerformance, PlayerPerformanceAdmin)
admin.site.register(TeamCode, TeamCodeModelAdmin)
admin.site.register(ScoreKeeperGame, ScoreKeeperGameAdmin)
