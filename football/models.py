from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Sum

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
        verbose_name = "Football Gender League Type"

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
        verbose_name = "Football Team Code"

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
    draws = models.IntegerField(null=True, blank=True)
    points=models.IntegerField(null=True, blank=True)
    goals_for=models.IntegerField(null=True, blank=True)
    goals_against=models.IntegerField(null=True, blank=True)
    goals_difference=models.IntegerField(null=True, blank=True)

    def __str__(self):
       return f"{self.team_gender}: {self.team_name}"
    
    class Meta:
        verbose_name = "Football Team"   


def validate_future_date(value):
    if value < timezone.now().date():
        raise ValidationError("Game date must be today or later.")


class Game(models.Model):
    GAME_STATUS_CHOICES = [
        ('Soon', 'Soon'),
        ('First Half', 'First Half'),
        ('Half Time', 'Half Time'),
        ('Second Half', 'Second Half'),
        ('Final', 'Final'),
    ]

    game_id = models.AutoField(primary_key=True)
    game_location = models.CharField(max_length=255, null=True)
    game_time = models.TimeField(null=True, blank=True)
    team_1 = models.ForeignKey(
        Team, related_name='football_team_1_games', on_delete=models.CASCADE)
    team_2 = models.ForeignKey(
        Team, related_name='football_team_2_games', on_delete=models.CASCADE)
    game_status = models.CharField(
        max_length=20, choices=GAME_STATUS_CHOICES, default='Soon')
    game_date = models.DateField()
    team_1_score = models.IntegerField(null=True, blank=True)
    team_2_score = models.IntegerField(null=True, blank=True)
    team_won = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='football_team_won', null=True, blank=True)
    team_lost = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='football_team_lost', null=True, blank=True)
    team_1_draw = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='football_team_1_draw', null=True, blank=True)
    team_2_draw= models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='football_team_2_draw', null=True, blank=True)
    
    
    class Meta:
        verbose_name = "Football Game"

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
    player_image = models.ImageField(upload_to='player_images/', blank=True,default='images/person-placeholder.png')
    player_shirt_number = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name="football_player_team")
    goals = models.IntegerField(null=True, blank=True)
    own_goals = models.IntegerField(null=True, blank=True)  
    assists = models.IntegerField(null=True, blank=True)
    shots_on_goal= models.IntegerField(null=True, blank=True)
    tackles = models.IntegerField(null=True, blank=True)
    crosses= models.IntegerField(null=True, blank=True)
    saves = models.IntegerField(null=True, blank=True)
    penalty_kicks = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Football Player"

    def __str__(self):
        return f"{self.player_first_name} {self.player_last_name} , {self.team.team_name} team"



class ScoreKeeper(models.Model):
    keeper_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="footable_keeper_user")
    keeper_number = models.BigIntegerField()

    def __str__(self):
        return f"{self.keeper_number}, {self.user}"
    class Meta:
        verbose_name = "Football Score Keeper"


class ScoreKeeperGame(models.Model):
    score_keeper = models.ForeignKey(ScoreKeeper, on_delete=models.CASCADE,related_name="football_scorekeeper")
    game = models.ForeignKey(Game, on_delete=models.CASCADE,related_name="football_game")

    class Meta:
        unique_together = ('game', 'score_keeper')
        verbose_name = "Football Score Keeper Game"

    def __str__(self):
        return f"{self.score_keeper}, {self.game.team_1.team_name} vs {self.game.team_2.team_name} on {self.game.game_date}"


class PlayerPerformance(models.Model):
   
    performance_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE,related_name="football_playerperformance_set")
    player = models.ForeignKey(Player, on_delete=models.CASCADE,related_name="football_playerperformance_set")
    goals = models.IntegerField(null=True, blank=True) 
    own_goals = models.IntegerField(null=True, blank=True)   
    assists = models.IntegerField(null=True, blank=True)
    shots_on_goal= models.IntegerField(null=True, blank=True)
    tackles = models.IntegerField(null=True, blank=True)
    crosses = models.IntegerField(null=True, blank=True)
    saves = models.IntegerField(null=True, blank=True)
    penalty_kicks = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('game', 'player')
        verbose_name = "Football Player Performance"

    def __str__(self):
        return f"{self.player.player_first_name} {self.player.player_last_name} , {self.game.team_1.team_name} vs {self.game.team_2.team_name} on {self.game.game_date}"

   
