from django.contrib import admin
from .models import *


class TeamCodeModelAdmin(admin.ModelAdmin):
    list_display = ['team_code',
                    'team_code_expiry_date', 'team_code_used']


class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'team_abbreviation', 'team_logo', 'manager_first_name',
                    'manager_last_name', 'manager_phone_number', 'manager_email', 'wins', 'loses']
    search_fields = ['team_name', 'manager_first_name']


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['player_first_name', 'player_last_name', 'player_date_of_birth',
                    'player_phone_number', 'player_shirt_number','player_email', 'player_image', 'team']
    search_fields = ['player_first_name', 'player_last_name',
                    'player_phone_number', 'player_shirt_number','player_email',  'team']


class ScoreKeeperAdmin(admin.ModelAdmin):
    list_display = ['keeper_id', 'user', 'keeper_number']
    search_fields = ['keeper_id', 'user' 'keeper_number']


class ScoreKeeperGameAdmin(admin.ModelAdmin):
    list_display = ['id', 'score_keeper', 'game', ]
    search_fields = ['score_keeper', 'game']


class GameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'sets','game_location', 'team_1', 'team_2',
                    'game_status', 'game_date', 'team_1_score', 'team_2_score', 'team_won', 'team_lost']
    search_fields = ['game_id',
                     'game_location', 'team_1__team_name', 'team_2__team_name']

class VolleyballSetAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    list_display = ['set_id', 'set_number','game', 'team_1_points', 'team_2_points']
    search_fields = ['set_id', 'game']

class PlayerPerformanceAdmin(admin.ModelAdmin):
    list_display = ['performance_id','volleyball_set', 'player', 'attack_attempts','kills','errors',
                    'digs', 'blocks', 'solo_blocks_and_assisted_blocks', 'service_aces',]
    search_fields = ['performance_id', 'volleyball_set', 'player']


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(ScoreKeeper, ScoreKeeperAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(VolleyballSet, VolleyballSetAdmin)
admin.site.register(PlayerPerformance, PlayerPerformanceAdmin)
admin.site.register(TeamCode, TeamCodeModelAdmin)
admin.site.register(ScoreKeeperGame, ScoreKeeperGameAdmin)
