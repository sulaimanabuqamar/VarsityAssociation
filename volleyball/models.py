from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

class GenderLeagueType(models.Model):
    genders_choices=[
        ('Men','Men'),
        ('Women','Women'),
    ]
    image = models.ImageField(
        upload_to='langing_pages_images/', blank=True, null=True)
    gender=models.CharField(
        max_length=20, choices=genders_choices, default='Men',)
    
    class Meta:
        unique_together = ['gender']
        verbose_name = "Volleyball Gender League Type"

    def __str__(self):
        return f'{self.gender}'


class TeamCode(models.Model):
    team_code_id = models.AutoField(primary_key=True)
    team_code = models.CharField(
        max_length=7, help_text='Code must be in format XXX-XXX. all in capital letters')
    team_code_expiry_date = models.DateField(default=timezone.now().date(
    ) + timedelta(days=7), help_text='Default is 7 days from now')
    team_code_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Volleyball Team Code"

    def __str__(self):
        return f'{self.team_code} expires: {self.team_code_expiry_date}'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_gender=models.CharField(
        max_length=20, choices=GenderLeagueType.genders_choices, default='Men')
    team_name = models.CharField(max_length=40)
    team_abbreviation = models.CharField(max_length=4)
    team_logo = models.ImageField(upload_to='team_logos/')
    manager_first_name = models.CharField(max_length=25)
    manager_last_name = models.CharField(max_length=25)
    manager_phone_number = models.IntegerField()
    manager_email = models.EmailField()
    wins = models.IntegerField(null=True, blank=True)
    loses = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.team_gender}: {self.team_name}"
    
    class Meta:
        verbose_name = "Volleyball Team"

def validate_future_date(value):
    if value < timezone.now().date():
        raise ValidationError("Game date must be today or later.")


class Game(models.Model):
    GAME_STATUS_CHOICES = [
        ('Soon', 'Soon'),
        ('Set 1', 'Set 1'),
        ('Set 2', 'Set 2'),
        ('Set 3', 'Set 3'),
        ('Set 4', 'Set 4}'),
        ('Set 5', 'Set 5'),
        ('Final', 'Final'),
    ]
    SETS_CHOICES=[
        (1,1),
        (3,3),
         (5,5),
    ]
    game_id = models.AutoField(primary_key=True)
    sets=models.IntegerField(choices=SETS_CHOICES)
    game_location = models.CharField(max_length=255, null=True)
    game_time = models.TimeField(null=True, blank=True)
    team_1 = models.ForeignKey(
        Team, related_name='volleyball_team_1_games', on_delete=models.CASCADE)
    team_2 = models.ForeignKey(
        Team, related_name='volleyball_team_2_games', on_delete=models.CASCADE)
    game_status = models.CharField(
        max_length=20, choices=GAME_STATUS_CHOICES, default='Soon')
    game_date = models.DateField()
    team_1_score = models.IntegerField(null=True, blank=True)
    team_2_score = models.IntegerField(null=True, blank=True)
    team_won = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='volleyball_team_won', null=True, blank=True)
    team_lost = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='volleyball_team_lost', null=True, blank=True)
   
    
    
    class Meta:
        verbose_name = "Volleyball Game"

    def __str__(self):
        return f" {self.team_1.team_name} vs {self.team_2.team_name} on {self.game_date}"
    
    
   

    def clean(self):
        if self.pk is None:
            validate_future_date(self.game_date)

        if self.team_1 == self.team_2:
            raise ValidationError('Team 1 and Team 2 cannot be the same.')

        if self.team_won is None and self.team_lost is None:
            # Both team_won and team_lost are null, so we can save without error
            return

        # Validate that team_won and team_lost are either team_1 or team_2
        elif self.team_won not in [self.team_1, self.team_2] or self.team_lost not in [self.team_1, self.team_2]:
            raise ValidationError(
                "Team won and team lost  must be either team 1 or team 2")

        elif self.team_won == self.team_lost:
            raise ValidationError("Team won and lost cannot be the same")
        
   

    def save(self, *args, **kwargs):
        self.full_clean()  # Run the clean method to perform validation
        super(Game, self).save(*args, **kwargs)
    
 


class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    player_first_name = models.CharField(max_length=25,null=True, blank=True)
    player_last_name = models.CharField(max_length=25,null=True, blank=True)
    player_date_of_birth = models.DateField(null=True, blank=True)
    player_phone_number = models.IntegerField(null=True, blank=True)
    player_email = models.EmailField(max_length=25,null=True, blank=True)
    player_image = models.ImageField(upload_to='player_images/',null=True, blank=True,default='images/person-placeholder.png')
    player_shirt_number = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="volleyball_player_team")
    attack_attempts= models.IntegerField(null=True, blank=True)   
    kills = models.IntegerField(null=True, blank=True)
    errors= models.IntegerField(null=True, blank=True)
    digs= models.IntegerField(null=True, blank=True)
    blocks= models.IntegerField(null=True, blank=True)
    solo_blocks_and_assisted_blocks= models.IntegerField(null=True, blank=True)
    service_aces= models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Volleyball Player"

    def __str__(self):
        return f"{self.player_first_name} {self.player_last_name} , {self.team.team_name} team"



class ScoreKeeper(models.Model):
    keeper_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="volleyball_keeper_user")
    keeper_number = models.BigIntegerField()

    def __str__(self):
        return f"{self.keeper_number}, {self.user}"
    class Meta:
        verbose_name = "Volleyball Score Keeper"


class ScoreKeeperGame(models.Model):
    score_keeper = models.ForeignKey(ScoreKeeper, on_delete=models.CASCADE,related_name="volleyball_scorekeeper")
    game = models.ForeignKey(Game, on_delete=models.CASCADE,related_name="volleyball_game")

    class Meta:
        unique_together = ('game', 'score_keeper')
        verbose_name = "Volleyball Score Keeper Game"

    def __str__(self):
        return f"{self.score_keeper.user}, {self.game.team_1.team_name} vs {self.game.team_2.team_name} on {self.game.game_date}"

class VolleyballSet(models.Model):
    set_id=models.AutoField(primary_key=True)
    set_number= models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE,related_name="volleyball_set")
    team_1_points= models.IntegerField(null=True, blank=True)
    team_2_points= models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('set_number', 'game')
        verbose_name = "Volleyball Set"
    
    def clean(self):
        super().clean()

        # Check if set_number is within the valid range specified by the related Game instance
        if self.set_number < 1 or self.set_number > self.game.sets:
            raise ValidationError(f"Set number must be range between 1 to {self.game.sets}")
    def __str__(self):
        return f"set: {self.set_number} ,{self.game.team_1.team_name} vs {self.game.team_2.team_name} on {self.game.game_date}"


class PlayerPerformance(models.Model):
   
    performance_id = models.AutoField(primary_key=True)
    volleyball_set= models.ForeignKey(VolleyballSet, on_delete=models.CASCADE,related_name="volleyball_playerperformance_set")
    player = models.ForeignKey(Player, on_delete=models.CASCADE,related_name="volleyball_playerperformance_set")
    attack_attempts= models.IntegerField(null=True, blank=True)   
    kills = models.IntegerField(null=True, blank=True)
    errors= models.IntegerField(null=True, blank=True)
    digs= models.IntegerField(null=True, blank=True)
    blocks= models.IntegerField(null=True, blank=True)
    solo_blocks_and_assisted_blocks= models.IntegerField(null=True, blank=True)
    service_aces= models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('volleyball_set', 'player')
        verbose_name = "Volleyball Player Performance"

    def __str__(self):
        return f"{self.player.player_first_name} {self.player.player_last_name} , set: {self.volleyball_set.set_number} ,{self.volleyball_set.game.team_1.team_name} vs {self.volleyball_set.game.team_2.team_name} on {self.volleyball_set.game.game_date}"

   


