from django.db.models.signals import post_delete, post_save,pre_save
from django.dispatch import receiver
from .models import *
import os
from django.conf import settings

@receiver(pre_save, sender=GenderLeagueType)
def delete_previous_image(sender, instance, **kwargs):
    # Check if the instance already has an ID, meaning it's an update
    if instance.id:
        try:
            # Get the existing instance from the database
            existing_instance = GenderLeagueType.objects.get(id=instance.id)

            # Check if the image field has changed
            if existing_instance.image and existing_instance.image != instance.image:
                # Delete the previous image file
                if os.path.isfile(existing_instance.image.path):
                    os.remove(existing_instance.image.path)
        except GenderLeagueType.DoesNotExist:
            pass  # Instance doesn't exist yet, nothing to delete

@receiver(post_delete, sender=GenderLeagueType)
def delete_image_on_delete(sender, instance, **kwargs):
    # Delete the image file when the model instance is deleted
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


# Define a signal to update after  game has been deleted deleted
@receiver(post_delete, sender=Game)
def update_player_and_team_after_game_delete(sender, instance, **kwargs):
    for player_performance in PlayerPerformance.objects.filter(game=instance):
        update_player(player_performance.player)
    update_team_wins_loses(instance.team_1)
    update_team_wins_loses(instance.team_2)


#delete image if does not merge the current logo
@receiver(pre_save, sender=Team)
def delete_previous_logo(sender, instance, **kwargs):
    # Check if the instance already exists in the database
    if instance.pk:
        original_team = Team.objects.get(pk=instance.pk)
        # Check if the logo has changed
        if original_team.team_logo != instance.team_logo:
            # Delete the previous logo file
            if original_team.team_logo:
                if os.path.isfile(original_team.team_logo.path):
                    os.remove(original_team.team_logo.path)


#delete image if does not merge the current player image
@receiver(pre_save, sender=Player)
def delete_previous_image(sender, instance, **kwargs):
    # Check if the player_image has changed and it's not the default image
    if instance.pk:
        original_player = Player.objects.get(pk=instance.pk)
        if original_player.player_image and  original_player.player_image.name != instance.player_image.name and \
                not original_player.player_image.name.endswith('person-placeholder.png'):
            # Delete the previous image file
            if os.path.isfile(original_player.player_image.path):
                os.remove(original_player.player_image.path)


# Define a signal to update the game when a player's performance is updated
@receiver(post_save, sender=PlayerPerformance)
def update_after_player_performance_save(sender, instance, **kwargs):
    player = instance.player
    update_player(player)
    update_game(instance.game)
    update_team_wins_loses(instance.game.team_1)
    update_team_wins_loses(instance.game.team_2)

# Define a signal to update  a player's performance is deleted


@receiver(post_delete, sender=PlayerPerformance)
def update_after_player_performance_delete(sender, instance, **kwargs):
    player = instance.player
    update_player(player)
    update_game(instance.game)
    update_team_wins_loses(instance.game.team_1)
    update_team_wins_loses(instance.game.team_2)


def update_player(player):
    player.field_goals = player.playerperformance_set.filter(field_goals__isnull=False).aggregate(Sum('field_goals'))[
        'field_goals__sum']
    player.three_pointers = player.playerperformance_set.filter(three_pointers__isnull=False).aggregate(Sum('three_pointers'))[
        'three_pointers__sum']
    player.free_throws = player.playerperformance_set.filter(free_throws__isnull=False).aggregate(Sum('free_throws'))[
        'free_throws__sum']
    player.rebounds = player.playerperformance_set.filter(rebounds__isnull=False).aggregate(Sum('rebounds'))[
        'rebounds__sum']
    player.assists = player.playerperformance_set.filter(assists__isnull=False).aggregate(Sum('assists'))[
        'assists__sum']
    player.steals = player.playerperformance_set.filter(steals__isnull=False).aggregate(Sum('steals'))[
        'steals__sum']
    player.blocks = player.playerperformance_set.filter(blocks__isnull=False).aggregate(Sum('blocks'))[
        'blocks__sum']
    player.turnovers = player.playerperformance_set.filter(turnovers__isnull=False).aggregate(Sum('turnovers'))[
        'turnovers__sum']
    player.points = player.playerperformance_set.filter(points__isnull=False).aggregate(Sum('points'))[
        'points__sum']

    check_field_goals = player.playerperformance_set.filter(
        field_goals__isnull=False)
    check_three_pointers = player.playerperformance_set.filter(
        three_pointers__isnull=False)
    check_free_throws = player.playerperformance_set.filter(
        free_throws__isnull=False)

    if check_field_goals:
        player.field_goals_percentage = player.playerperformance_set.filter(field_goals__isnull=False).aggregate(Sum('field_goals'))[
            'field_goals__sum'] / player.playerperformance_set.filter(field_goals__isnull=False).count()
    if check_three_pointers:
        player.three_pointers_percentage = player.playerperformance_set.filter(three_pointers__isnull=False).aggregate(Sum('three_pointers'))[
            'three_pointers__sum'] / player.playerperformance_set.filter(three_pointers__isnull=False).count()
    if check_free_throws:
        player.free_throws_percentage = player.playerperformance_set.filter(free_throws__isnull=False).aggregate(Sum('free_throws'))[
            'free_throws__sum'] / player.playerperformance_set.filter(free_throws__isnull=False).count()

    player.save()


def update_game(game):

    team_1_score = 0
    team_2_score = 0
    team_won = None
    team_lost = None

    # Calculate the total points for team 1 and team 2
    for performance in game.playerperformance_set.filter(points__isnull=False).all():
        if performance.player.team == game.team_1:
            team_1_score += performance.points

        elif performance.player.team == game.team_2:
            team_2_score += performance.points
   

    # Determine the winning and losing teams    
    if team_1_score > team_2_score:
        team_won = game.team_1
        team_lost = game.team_2

    elif team_2_score > team_1_score:
        team_won = game.team_2
        team_lost = game.team_1

    # Update the game model
    game.team_won = team_won
    game.team_lost = team_lost
    game.team_1_score = team_1_score
    game.team_2_score = team_2_score
    game.save()


def update_team_wins_loses(team):
    wins = Game.objects.filter(team_won=team).count()
    loses = Game.objects.filter(team_lost=team).count()

    if wins or loses:
        team.wins = wins
        team.loses = loses

    else:
        team.wins = None
        team.loses = None

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
    if file_field and file_field!= 'images/person-placeholder.png':
        # Get the path to the media file
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_field))
        # Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
            os.remove(file_path)


