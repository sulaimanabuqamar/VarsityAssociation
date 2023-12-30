from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import *
from django.db.models import Q
import os
from django.conf import settings

# Define a signal to update after  game has been deleted deleted


@receiver(post_delete, sender=Game)
def update_player_and_team_after_game_delete(sender, instance, **kwargs):
    for player_performance in PlayerPerformance.objects.filter(game=instance):
        update_player(player_performance.player)
    update_team_wins_draws_loses(instance.team_1)
    update_team_wins_draws_loses(instance.team_2)

# Define a signal to update the game when a player's performance is updated


@receiver(post_save, sender=PlayerPerformance)
def update_after_player_performance_save(sender, instance, **kwargs):
    player = instance.player
    update_player(player)
    update_game(instance.game)
    update_team_wins_draws_loses(instance.game.team_1)
    update_team_wins_draws_loses(instance.game.team_2)

# Define a signal to update  a player's performance is deleted


@receiver(post_delete, sender=PlayerPerformance)
def update_after_player_performance_delete(sender, instance, **kwargs):
    player = instance.player
    update_player(player)
    update_game(instance.game)
    update_team_wins_draws_loses(instance.game.team_1)
    update_team_wins_draws_loses(instance.game.team_2)


def update_player(player):
    player.goals = player.football_playerperformance_set.filter(goals__isnull=False).aggregate(Sum('goals'))[
        'goals__sum']  
    player.own_goals = player.football_playerperformance_set.filter(own_goals__isnull=False).aggregate(Sum('own_goals'))[
        'own_goals__sum']  
    player.assists = player.football_playerperformance_set.filter(assists__isnull=False).aggregate(Sum('assists'))[
        'assists__sum']
    player.shots_on_goal = player.football_playerperformance_set.filter(shots_on_goal__isnull=False).aggregate(Sum('shots_on_goal'))[
        'shots_on_goal__sum']
    player.tackles= player.football_playerperformance_set.filter(tackles__isnull=False).aggregate(Sum('tackles'))[
        'tackles__sum']
    player.crosses = player.football_playerperformance_set.filter(crosses__isnull=False).aggregate(Sum('crosses'))[
        'crosses__sum']
    player.penalty_kicks= player.football_playerperformance_set.filter(penalty_kicks__isnull=False).aggregate(Sum('penalty_kicks'))[
        'penalty_kicks__sum']
    player.saves= player.football_playerperformance_set.filter(saves__isnull=False).aggregate(Sum('saves'))[
        'saves__sum']
    player.save()


def update_game(game):

    team_1_score = 0
    team_2_score = 0
    team_won = None
    team_lost = None
    team_1_draw=None
    team_2_draw=None

    # Calculate the total goals for team 1 and team 2
    for performance in game.football_playerperformance_set.filter(Q(goals__isnull=False) | Q(own_goals__isnull=False)).all():
        if performance.player.team == game.team_1:
            team_1_score += performance.goals or 0
            team_2_score+= performance.own_goals or 0
        elif performance.player.team == game.team_2:
            team_2_score += performance.goals or 0
            team_1_score += performance.own_goals or 0
    
    # Determine the winning and losing teams
  
    if team_1_score > team_2_score:
        team_won = game.team_1
        team_lost = game.team_2

    elif team_2_score > team_1_score:
        team_won = game.team_2
        team_lost = game.team_1
    else:
        team_1_draw=game.team_1
        team_2_draw=game.team_2

    # Update the game model
    game.team_won = team_won
    game.team_lost = team_lost
    game.team_1_draw= team_1_draw
    game.team_2_draw = team_2_draw
    game.team_1_score = team_1_score
    game.team_2_score = team_2_score
    game.save()


def update_team_wins_draws_loses(team):
    wins = Game.objects.filter(team_won=team).count()
    loses = Game.objects.filter(team_lost=team).count()
    draws = Game.objects.filter(Q(team_1_draw=team) | Q(team_2_draw=team)).count()

    # Calculate goals for and against
    goals_for = sum([game.team_1_score for game in Game.objects.filter(Q(team_won=team) | Q(team_1_draw=team))])
    goals_against = sum([game.team_2_score for game in Game.objects.filter(Q(team_lost=team) | Q(team_2_draw=team))])

    if wins or loses or draws:
        team.wins = wins
        team.loses = loses
        team.draws = draws
        team.goals_for = goals_for
        team.goals_against = goals_against
        team.goals_difference = goals_for - goals_against

        # Calculate points: 3 points for a win, 1 point for a draw
        team.points = (3 * wins) + draws
    else:
        team.wins = None
        team.loses = None
        team.draws = None
        team.goals_for = None
        team.goals_against = None
        team.goals_difference = None
        team.points = None

    team.save()


# Signal handler to delete associated media files after the model instance is deleted
@receiver(post_delete, sender=Team)
def delete_media_files(sender, instance, **kwargs):
    file_field = instance.team_logo
    if file_field:
        # Get the path to the media file
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_field))
        # Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
            os.remove(file_path)

@receiver(post_delete, sender=Player)
def delete_media_files(sender, instance, **kwargs):
    file_field = instance.player_image
    if file_field:
        # Get the path to the media file
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_field))
        # Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
            os.remove(file_path)
