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
        upload_to='images/', blank=True, null=True)
    gender=models.CharField(
        max_length=20, choices=genders_choices, default='Men',)
    
    class Meta:
        unique_together = ['gender']

class TeamCode(models.Model):
    team_code_id = models.AutoField(primary_key=True)
    team_code = models.CharField(
        max_length=7, help_text='Code must be in format XXX-XXX. all in capital letters')
    team_code_expiry_date = models.DateField(default=timezone.now().date(
    ) + timedelta(days=7), help_text='Default is 7 days from now')
    team_code_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Basketball Team Code"

    def __str__(self):
        return f'{self.team_code} expires: {self.team_code_expiry_date}'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=40)
    team_abbreviation = models.CharField(max_length=4)
    team_logo = models.ImageField(upload_to='team_logos/')
    manager_first_name = models.CharField(max_length=25)
    manager_last_name = models.CharField(max_length=25)
    manager_phone_number = models.IntegerField()
    manager_email = models.EmailField()
    wins = models.IntegerField(null=True, blank=True)
    loses = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Basketball Team"

    def __str__(self):
        return f"{self.team_name}"

def validate_future_date(value):
    if value < timezone.now().date():
        raise ValidationError("Game date must be today or later.")


class Game(models.Model):
    GAME_STATUS_CHOICES = [
        ('Soon', 'Soon'),
        ('Q1', 'Quarter 1'),
        ('Q2', 'Quarter 2'),
        ('Halftime', 'Halftime'),
        ('Q3', 'Quarter 3'),
        ('Q4', 'Quarter 4'),
        ('Final', 'Final'),
    ]

    game_id = models.AutoField(primary_key=True)
    game_location = models.CharField(max_length=255, null=True)
    game_time = models.TimeField(null=True, blank=True)
    team_1 = models.ForeignKey(
        Team, related_name='team_1_games', on_delete=models.CASCADE)
    team_2 = models.ForeignKey(
        Team, related_name='team_2_games', on_delete=models.CASCADE)
    game_status = models.CharField(
        max_length=20, choices=GAME_STATUS_CHOICES, default='Soon')
    game_date = models.DateField()
    team_1_score = models.IntegerField(null=True, blank=True)
    team_2_score = models.IntegerField(null=True, blank=True)
    team_won = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='team_won', null=True, blank=True)
    team_lost = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='team_lost', null=True, blank=True)
    
    class Meta:
        verbose_name = "Basketball Team Game"

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
    player_first_name = models.CharField(max_length=25)
    player_last_name = models.CharField(max_length=25)
    player_date_of_birth = models.DateField()
    player_phone_number = models.IntegerField()
    player_email = models.EmailField(max_length=25)
    player_image = models.ImageField(upload_to='player_images/',null=True, blank=True,default='images/person-placeholder.png')
    player_shirt_number = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    field_goals = models.IntegerField(null=True, blank=True)
    field_goals_percentage = models.FloatField(
        null=True, blank=True)
    three_pointers = models.IntegerField(null=True, blank=True)
    three_pointers_percentage = models.FloatField(
        null=True, blank=True)
    free_throws = models.IntegerField(null=True, blank=True)
    free_throws_percentage = models.FloatField(
        null=True, blank=True)
    rebounds = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    steals = models.IntegerField(null=True, blank=True)
    blocks = models.IntegerField(null=True, blank=True)
    turnovers = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Basketball Player"

    def __str__(self):
        return f"{self.player_first_name} {self.player_last_name} , {self.team.team_name} team"


class ScoreKeeper(models.Model):
    keeper_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    keeper_number = models.BigIntegerField()

    class Meta:
        verbose_name = "Basketball Score Keeper"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class ScoreKeeperGame(models.Model):
    score_keeper = models.ForeignKey(ScoreKeeper, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'score_keeper')
        verbose_name = "Basketball Score Keeper Game"

    def __str__(self):
        return f"{self.score_keeper.user.first_name}  {self.score_keeper.user.last_name} , {self.game.team_1.team_name} vs {self.game.team_2.team_name} on {self.game.game_date}"


class PlayerPerformance(models.Model):
    performance_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    field_goals = models.IntegerField(null=True, blank=True, )
    three_pointers = models.IntegerField(null=True, blank=True)
    free_throws = models.IntegerField(null=True, blank=True)
    rebounds = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    steals = models.IntegerField(null=True, blank=True)
    blocks = models.IntegerField(null=True, blank=True)
    turnovers = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('game', 'player')
        verbose_name = "Basketball Player Peformance"

    def __str__(self):
        return f"{self.player.player_first_name} {self.player.player_last_name} , {self.game.team_1.team_name} vs {self.game.team_2.team_name} on {self.game.game_date}"

    def save(self, *args, **kwargs):
        points = None
        if self.field_goals is not None or self.three_pointers is not None or self.free_throws is not None:
            # Calculate 'points'
            points = int(self.field_goals or 0) * 2 + \
                int(self.three_pointers or 0) * \
                3 + int(self.free_throws or 0)
            # Calculate 'points'
        self.points = points

        super(PlayerPerformance, self).save(*args, **kwargs)




