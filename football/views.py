from django.shortcuts import redirect, render
from django.urls import reverse
from django.db.models.functions import TruncMonth
from .forms import PlayerForm, TeamForm
from django.contrib import messages
from django import forms
from .models import *
from .decorators import custom_login_required
from django.db.models import Sum, Count, Q, F, ExpressionWrapper, FloatField
from django.views.decorators.http import require_POST
from django.db.models.functions import Coalesce
from django.forms import formset_factory
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.serializers import serialize
import json

# Create your views here.
def selectGender(request):
    
    gender=request.GET.get('gender') 
    if gender:
        if gender=='Women':
            request.session['team_gender']='Women' 
        else:
            request.session['team_gender']='Men'
            
        if request.user.is_authenticated: 
            return redirect('football-adminSchedule') 
        return redirect('football-schedule')
    

    page_data=GenderLeagueType.objects.all()
    return render(request,'football/select-gender.html',{'page_data':page_data})  



# used loginUser since login function is built function
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('football-adminSchedule')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login only staff
            if user.is_staff:
                login(request, user)
                return redirect('football-adminSchedule')
            else:
                messages.error(
                    request, 'You are not staff')

        else:
            messages.error(
                request, 'Invalid login credentials. Please try again.')

    return render(request, 'base/Login.html')

def about(request):
    return render(request, "football/About.html", {'title': 'About Us'})


def privacy(request):
    return render(request, "football/Privacy.html", {'title': 'Privacy'})


def terms(request):
    return render(request, "football/Terms.html", {'title': 'Terms'})


def FAQs(request):
    return render(request, "football/FAQs.html", {'title': 'FAQ'})

@require_POST
def verifyTeamCode(request):
    team_code = request.POST.get('team_code')
    if not team_code:
        return JsonResponse('error', 'please enter the whole code')

    check_code = TeamCode.objects.filter(
        team_code=team_code, team_code_expiry_date__gt=timezone.now(), team_code_used=False)

    if not check_code:
        return JsonResponse({'error': 'The code has either expired or does not exist'})
    return JsonResponse({'success': 'The code verified successfully. You can now enter team details '})


def schedule(request):
    team_gender=request.session.get('team_gender')
    games = Game.objects.filter(Q(team_1__team_gender=team_gender)|Q(team_2__team_gender=team_gender))
    grouped_months = games.annotate(month=TruncMonth('game_date')).values(
        'month').annotate(data_count=Count('game_id')).order_by('month')
    games_per_month = {}
    # group each game per month
    for item in grouped_months:

        games_per_month[item['month'].strftime('%B')] = games.filter(
            game_date__month=item['month'].strftime('%m'))

    return render(request, "football/Schedule.html", {'games_per_month': games_per_month, 'title': 'Schedule'})


@ custom_login_required
def adminSchedule(request):
    team_gender=request.session.get('team_gender')
    # super user can access all games otherwise check  games assigned to user
    if request.user.is_superuser:
        games = Game.objects.filter(Q(team_1__team_gender=team_gender)|Q(team_2__team_gender=team_gender))
    else:
        games = Game.objects.filter(
              Q(team_1__team_gender=team_gender)|Q(team_2__team_gender=team_gender),
            scorekeepergame__score_keeper__user=request.user)
    grouped_months = games.annotate(month=TruncMonth('game_date')).values(
        'month').annotate(data_count=Count('game_id')).order_by('month')
    games_per_month = {}
    for item in grouped_months:

        games_per_month[item['month'].strftime('%B')] = games.filter(
            game_date__month=item['month'].strftime('%m'))

    return render(request, "football/AdminSchedule.html", {'games_per_month': games_per_month, 'title': 'Admin Schedule'})


def teams(request):
    team_gender=request.session.get('team_gender')
    teams = Team.objects.filter(team_gender=team_gender).order_by('-points', '-goals_difference')
    return render(request, "football/Teams.html", {'teams': teams, 'title': 'teams'})


def stats(request):
    team_gender=request.session.get('team_gender')
    goal_leaders = Player.objects.filter(team__team_gender=team_gender,goals__gt=0).order_by('-goals')[:5]
    assist_leaders = Player.objects.filter(
        team__team_gender=team_gender,
        assists__gt=0).order_by('-assists')[:5]
    saves_leaders = Player.objects.filter(
        team__team_gender=team_gender,
        saves__gt=0).order_by('-saves')[:5]
    context = {
        'title': 'Stats',
        'goal_leaders': goal_leaders,
        'assist_leaders': assist_leaders,
        'saves_leaders': saves_leaders,
    }

    return render(request, "football/Stats.html", context)


def add_team(request):
    code_error = True
    if request.method == 'POST':
        team_code = request.POST.get('team_code')
        previous_url = request.POST.get('previous_url')
        check_code = TeamCode.objects.filter(
            team_code=team_code, team_code_expiry_date__gt=timezone.now(), team_code_used=False)
        # used modelformset for players since arrays forms needed to validated
        PlayerFormSet = forms.modelformset_factory(
            Player, form=PlayerForm, extra=1)
        team_form = TeamForm(request.POST, request.FILES)
        player_formset = PlayerFormSet(
            request.POST, request.FILES, queryset=Player.objects.none())
        if not check_code:
            code_error = True
            messages.error(
                request, 'The code has either expired or does not exist')

        else:
            code_error = False

            # if players less  than 7  raise  form error
            if len(player_formset) <7 or len(player_formset) >12:
                team_form.add_error(
                    None, "You must add minimum of 7 players")
            elif request.POST.get('check1') != 'on' or request.POST.get('check2') != 'on' or request.POST.get('check2') != 'on':
                team_form.add_error(
                    None, "Please check all checkboxes")
            else:
                if team_form.is_valid() and player_formset.is_valid():
                    team = team_form.save(commit=False)
                    team.team_gender=request.session.get('team_gender')
                    team.save()
                    for form in player_formset:
                        player = form.save(commit=False)
                        player.team = team
                        player.team_gender=request.session.get('team_gender')
                        player.save()
                    check_code.update(team_code_used=True)
                    messages.success(request,'Team added successfully.')
                    return redirect('football-teams')
                else:
                    team_form.add_error(
                        None, "Team not added")
            messages.error(request, 'Please scroll down and correct error(s)')
    else:
        previous_url = request.META.get('HTTP_REFERER') or reverse('football-teams')
        team_form = TeamForm()
        PlayerFormSet = forms.modelformset_factory(
            Player, form=PlayerForm, extra=1)
        player_formset = PlayerFormSet(queryset=Player.objects.none())

    context = {'team_form': team_form,
               'code_error': code_error,
               'title': 'Register',
               'player_formset': player_formset,
               'previous_url': previous_url,
               }
    return render(request, 'football/add-team.html', context)

def boxScore(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        players1_performance_dict = {}
        team1_players = Player.objects.filter(team=game.team_1)
        for player1 in team1_players:
            player1_performance = PlayerPerformance.objects.filter(
                player=player1, game=game).first()
            players1_performance_dict[player1] = player1_performance
        

        players2_performance_dict = {}
        team2_players = Player.objects.filter(team=game.team_2)
        for player2 in team2_players:
            player2_performance = PlayerPerformance.objects.filter(
                player=player2, game=game).first()
            players2_performance_dict[player2] = player2_performance
        context = {
            'players1_performance_dict': players1_performance_dict,
            'players2_performance_dict': players2_performance_dict,
            'game': game,
            'title': 'Boxscore',
        }
        return render(request, "football/Boxscore.html", context)

    except Game.DoesNotExist:
        messages.error(
            request, 'Game not found')
        return redirect('football-boxscore')


@ custom_login_required
def adminBoxScore(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        game_statuses = Game.GAME_STATUS_CHOICES
        # super user access any game
        if not request.user.is_superuser:
            keeper = ScoreKeeperGame.objects.filter(
                score_keeper__user=request.user, game=game)
            if not keeper:
                messages.error(
                    request, 'You are not allowed to edit .')
                return redirect('football-adminSchedule')

        players1_performance_dict = {}
       
        team1_players = Player.objects.filter(team=game.team_1)
        for player1 in team1_players:
            player1_performance = PlayerPerformance.objects.filter(
                player=player1, game=game).first()
            players1_performance_dict[player1] = player1_performance

        players2_performance_dict = {}
        team2_players = Player.objects.filter(team=game.team_2)
        for player2 in team2_players:
            player2_performance = PlayerPerformance.objects.filter(
                player=player2, game=game).first()
            players2_performance_dict[player2] = player2_performance
        context = {
            'players1_performance_dict': players1_performance_dict,
            'players2_performance_dict': players2_performance_dict,
            'game': game,
            'title': 'Admin Boxscore',
            'game_statuses': game_statuses,
        }
        return render(request, "football/AdminBoxscore.html", context)

    except Game.DoesNotExist:
        messages.error(
            request, 'Game not found')
        return redirect('football-adminSchedule')


def allStats(request):
    team_gender=request.session.get('team_gender')
    players = Player.objects.filter(team__team_gender=team_gender).order_by('-goals')
    return render(request, "football/AllStats.html", {'players': players, 'title': 'All Stats'})


def teamStats(request, team_id):
    try:
        team = Team.objects.get(pk=team_id)
        players = Player.objects.filter(team=team)
        context = {'players': players,
                   'title': team.team_name + ' Players stats',
                   'team': team
                   }
        return render(request, "football/team-stats.html", context)
    except Team.DoesNotExist:
        messages.error(
            request, 'Team not found')
        return redirect('football-teams')


@ custom_login_required
@ require_POST
def saveScores(request, game_id):
    try:
        #  handle DoesNotExist automatically
        game = Game.objects.get(pk=game_id)
        
        # Only superuser or authorized scorekeepers are allowed
        if not (request.user.is_superuser or ScoreKeeperGame.objects.filter(
                score_keeper__user=request.user, game=game).exists()):
            url = reverse('football-adminSchedule')
            return JsonResponse({'redirect': url})

        # Save game status if there is a change
        game_status_change = request.POST.get('game_status_change')
        if game_status_change == 'yes':
            game_status = request.POST.get('game_status')
            game.game_status = game_status
            game.save()
            game = Game.objects.get(pk=game_id)
            json_game=json.loads(serialize('json', [game]))[0]['fields']
            return JsonResponse({'success': 'Game status updated successfully','game':json_game})

        # Get user and input field
        player_id = request.POST.get('player_id')
        input_value = request.POST.get('input_value')
        input_value = input_value if input_value.isdigit() else None
        column = request.POST.get('column')
        allowed_columns = ['goals','assists','own_goals','shots_on_goal','tackles','crosses','saves','penalty_kicks']

        # Reject if column is not in allowed columns
        if column not in allowed_columns:
            return JsonResponse({'error': 'wrong field'})

        player = Player.objects.filter(player_id=player_id).first()
         
        if not player:
            return JsonResponse({'error': 'player not found'})

        if player.team not in [game.team_1, game.team_2]:
            return JsonResponse({'error': 'player not found in that game'})

        # Create performance for players if it does not exist
        if not PlayerPerformance.objects.filter(game=game, player=player).exists():
            team_1_players = Player.objects.filter(team=game.team_1)
            team_2_players = Player.objects.filter(team=game.team_2)

            for team_player in team_1_players:
                PlayerPerformance.objects.get_or_create(game=game, player=team_player)

            for team_player in team_2_players:
                PlayerPerformance.objects.get_or_create(game=game, player=team_player)

        performance = PlayerPerformance.objects.get(game=game, player=player)
        setattr(performance, column, input_value)
        performance.save()

        game = Game.objects.get(pk=game_id)
        json_game=json.loads(serialize('json', [game]))[0]['fields']

        # Return all performances for the game to update if there is a change made in another user or tab
        player_performances = PlayerPerformance.objects.filter(
            game=game).values('goals','own_goals','assists','shots_on_goal','tackles','crosses','saves','penalty_kicks')
        return JsonResponse({'success': 'Score Updated successfully', 'player_peformances': list(player_performances), 'game':json_game})

    except Game.DoesNotExist:
        messages.error(request, 'Game not found')
        url = reverse('football-adminSchedule')
        return JsonResponse({'redirect': url})
