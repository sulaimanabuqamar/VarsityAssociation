from django.db.models.signals import post_delete, post_save,post_init,pre_delete
from django.dispatch import receiver
from .models import *
from django.db.models import Q
import os
from django.conf import settings
from django.db import transaction


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

        
#signal to create sets 

@receiver(post_save, sender=Game)
def create_volleyball_sets(sender, instance, **kwargs):
    num_sets = instance.sets
    volley_sets = VolleyballSet.objects.filter(game=instance)
    vol_count = volley_sets.count()

    def create_sets():
        # Create sets for the game
        if vol_count < num_sets:
            for set_number in range(1, num_sets + 1):
                VolleyballSet.objects.get_or_create(
                    set_number=set_number,
                    game=instance
                )
        elif vol_count > num_sets:
            sets_to_delete = VolleyballSet.objects.filter(game=instance).order_by('-set_number')[:vol_count - num_sets]
            for set_to_delete in sets_to_delete:
                try:
                    set_to_delete.delete()
                except VolleyballSet.DoesNotExist:
                    # Handle the case where the set doesn't exist
                    pass

    # Use on_commit to defer the execution of queries until after the transaction is committed
    transaction.on_commit(create_sets)

            
# Define a signal to update after  game has been deleted deleted
@receiver(post_delete, sender=Game)
def update_player_and_team_after_game_delete(sender, instance, **kwargs):
    for player_performance in PlayerPerformance.objects.filter(volleyball_set__game=instance):
        update_player(player_performance.player)
    update_team_wins_loses(instance.team_1)
    update_team_wins_loses(instance.team_2)



# Define a signal to update the game when a player's performance is updated


@receiver(post_save, sender=PlayerPerformance)
def update_after_player_performance_save(sender, instance, **kwargs):
    player = instance.player
    update_player(player)
    update_set(instance.volleyball_set)
    update_team_wins_loses(instance.volleyball_set.game.team_1)
    update_team_wins_loses(instance.volleyball_set.game.team_2)

# Define a signal to update  a player's performance is deleted


@receiver(post_delete, sender=PlayerPerformance)
def update_after_player_performance_delete(sender, instance, **kwargs):
    player = instance.player    
    update_player(player)
    update_set(instance.volleyball_set)
    update_team_wins_loses(instance.volleyball_set.game.team_1)
    update_team_wins_loses(instance.volleyball_set.game.team_2)


def update_player(player):
    player.attack_attempts = player.volleyball_playerperformance_set.filter(attack_attempts__isnull=False).aggregate(Sum('attack_attempts'))[
        'attack_attempts__sum']  
    player.kills = player.volleyball_playerperformance_set.filter(kills__isnull=False).aggregate(Sum('kills'))[
        'kills__sum']  
    player.errors = player.volleyball_playerperformance_set.filter(errors__isnull=False).aggregate(Sum('errors'))[
        'errors__sum']
    player.digs = player.volleyball_playerperformance_set.filter(digs__isnull=False).aggregate(Sum('digs'))[
        'digs__sum']
    player.blocks= player.volleyball_playerperformance_set.filter(blocks__isnull=False).aggregate(Sum('blocks'))[
        'blocks__sum']
    player.solo_blocks_and_assisted_blocks = player.volleyball_playerperformance_set.filter(solo_blocks_and_assisted_blocks__isnull=False).aggregate(Sum('solo_blocks_and_assisted_blocks'))[
        'solo_blocks_and_assisted_blocks__sum']
    player.service_aces= player.volleyball_playerperformance_set.filter(service_aces__isnull=False).aggregate(Sum('service_aces'))[
        'service_aces__sum']
    player.save()

# update sets
def update_set(set_model):
    team_1_points=0
    team_2_points=0    
    # calculate sets points for each team
    for performance in set_model.volleyball_playerperformance_set.filter(Q(kills__isnull=False) | Q(service_aces__isnull=False)).all():
        if performance.player.team == set_model.game.team_1:
            team_1_points += performance.kills or 0
            team_1_points += performance.service_aces or 0
        elif performance.player.team == set_model.game.team_2:
            team_2_points += performance.kills or 0
            team_2_points += performance.service_aces or 0

    set_model.team_1_points=team_1_points
    set_model.team_2_points=team_2_points
    set_model.save()

    
    update_game(set_model.game)


# update game
def update_game(game):
    team_1_score = 0
    team_2_score = 0
    team_won = None
    team_lost = None

    # Calculate the  sets won by each team 
    for volley_set in game.volleyball_set.filter(Q(team_1_points__isnull=False) | Q(team_2_points__isnull=False)).all():
        if volley_set.team_1_points > volley_set.team_2_points :
            team_1_score +=1
        elif volley_set.team_2_points > volley_set.team_1_points:
            team_2_score += 1
           
    
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

