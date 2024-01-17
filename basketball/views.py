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
import json
from django.core.serializers import serialize

# Create your views here.
# used loginUser since login function is built function


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('adminSchedule')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login only staff
            if user.is_staff:
                login(request, user)
                return redirect('adminSchedule')
            else:
                messages.error(
                    request, 'You are not staff')

        else:
            messages.error(
                request, 'Invalid login credentials. Please try again.')

    return render(request, 'basketball/Login.html')

def about(request):
    return render(request, "basketball/About.html", {'title': 'About Us'})


def privacy(request):
    return render(request, "basketball/Privacy.html", {'title': 'Privacy'})


def terms(request):
    return render(request, "basketball/Terms.html", {'title': 'Terms'})


def FAQs(request):
    return render(request, "basketball/FAQs.html", {'title': 'FAQ'})

def selectGender(request):
    
    gender=request.GET.get('gender') 
    if gender:
        if gender=='Women':
            request.session['team_gender']='Women' 
        else:
            request.session['team_gender']='Men'
            
        if request.user.is_authenticated: 
            return redirect('adminSchedule') 
        return redirect('schedule')
    

    page_data=GenderLeagueType.objects.all()
    return render(request,'basketball/select-gender.html',{'page_data':page_data})        


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
    games = Game.objects.filter(  Q(team_1__team_gender=team_gender)|Q(team_2__team_gender=team_gender))
    grouped_months = games.annotate(month=TruncMonth('game_date')).values(
        'month').annotate(data_count=Count('game_id')).order_by('month')
    games_per_month = {}
    # group each game per month
    for item in grouped_months:
      

        games_per_month[item['month'].strftime('%B')] = games.filter(
            game_date__month=item['month'].strftime('%m'))

    return render(request, "basketball/Schedule.html", {'games_per_month': games_per_month, 'title': 'Schedule'})


@ custom_login_required
def adminSchedule(request):
    team_gender=request.session.get('team_gender')
    # super user can access all games otherwise check  games assigned to user
    if request.user.is_superuser:
        games = Game.objects.filter(Q(team_1__team_gender=team_gender)|Q(team_2__team_gender=team_gender))
    else:
        related_name = ScoreKeeperGame._meta.get_field('game').related_query_name()
        games = Game.objects.filter(
            Q(team_1__team_gender=team_gender) | Q(team_2__team_gender=team_gender),
            **{f'{related_name}__score_keeper__user': request.user}
        )
        c
    grouped_months = games.annotate(month=TruncMonth('game_date')).values(
        'month').annotate(data_count=Count('game_id')).order_by('month')
    games_per_month = {}
    for item in grouped_months:

        games_per_month[item['month'].strftime('%B')] = games.filter(
            game_date__month=item['month'].strftime('%m'))

    return render(request, "basketball/AdminSchedule.html", {'games_per_month': games_per_month, 'title': 'Admin Schedule'})


def teams(request):
    team_gender=request.session.get('team_gender')
    teams = Team.objects.filter(team_gender=team_gender).order_by('-wins', '-loses')
    return render(request, "basketball/Teams.html", {'teams': teams, 'title': 'teams'})


def stats(request):
    team_gender=request.session.get('team_gender')
    point_leaders = Player.objects.filter(team__team_gender=team_gender,points__gt=0).order_by('-points')[:5]
    assist_leaders = Player.objects.filter(team__team_gender=team_gender,
        assists__gt=0).order_by('-assists')[:5]
    rebound_leaders = Player.objects.filter(team__team_gender=team_gender,
        rebounds__gt=0).order_by('-rebounds')[:5]
    block_leaders = Player.objects.filter(team__team_gender=team_gender,blocks__gt=0).order_by('-blocks')[:5]
    steal_leaders = Player.objects.filter(team__team_gender=team_gender,steals__gt=0).order_by('-steals')[:5]
    three_pointer_leaders = Player.objects.filter(team__team_gender=team_gender,
        three_pointers__gt=0).order_by('-three_pointers')[:5]
    context = {
        'title': 'Stats',
        'point_leaders': point_leaders,
        'assist_leaders': assist_leaders,
        'rebound_leaders': rebound_leaders,
        'block_leaders': block_leaders,
        'steal_leaders': steal_leaders,
        'three_pointer_leaders': three_pointer_leaders
    }

    return render(request, "basketball/Stats.html", context)


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
           
        
            # if players less  than 5  raise  form error
            if len(player_formset) < 5 or len(player_formset) > 12:
                team_form.add_error(
                    None, "You must add minimum of 5 players")
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
                        player.save()
                    check_code.update(team_code_used=True)
                    messages.success(request,'Team added successfully.')
                    return redirect('teams')
                else:
                    team_form.add_error(
                        None, "Team not added")
            messages.error(request, 'Please scroll down and correct error(s)')
    else:
        previous_url = request.META.get('HTTP_REFERER') or reverse('teams')
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
    return render(request, 'basketball/add-team.html', context)

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
        return render(request, "basketball/Boxscore.html", context)

    except Game.DoesNotExist:
        messages.error(
            request, 'Game not found')
        return redirect('boxscore')


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
                return redirect('adminSchedule')

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
        return render(request, "basketball/AdminBoxscore.html", context)

    except Game.DoesNotExist:
        messages.error(
            request, 'Game not found')
        return redirect('adminSchedule')


def allStats(request):
    team_gender=request.session.get('team_gender')
    players = Player.objects.filter(team__team_gender=team_gender).order_by('-points')
    return render(request, "basketball/AllStats.html", {'players': players, 'title': 'All Stats'})


def teamStats(request, team_id):
    try:
        team = Team.objects.get(pk=team_id)
        players = Player.objects.filter(team=team)
        context = {'players': players,
                   'title': team.team_name + ' Players stats',
                   'team': team
                   }
        return render(request, "basketball/team-stats.html", context)
    except Team.DoesNotExist:
        messages.error(
            request, 'Team not found')
        return redirect('teams')


@ custom_login_required
@ require_POST
def saveScores(request, game_id):
    try:
        #  handle DoesNotExist automatically
        game = Game.objects.get(pk=game_id)
        
        # Only superuser or authorized scorekeepers are allowed
        if not (request.user.is_superuser or ScoreKeeperGame.objects.filter(
                score_keeper__user=request.user, game=game).exists()):
            url = reverse('adminSchedule')
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
        allowed_columns = ['field_goals', 'three_pointers', 'free_throws',
                            'rebounds', 'assists', 'steals', 'blocks', 'turnovers']

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
            game=game).values('assists', 'blocks', 'field_goals', 'free_throws', 'player_id', 'points', 'rebounds', 'steals', 'three_pointers', 'turnovers')
        return JsonResponse({'success': 'Score Updated successfully', 'player_peformances': list(player_performances), 'game':json_game})

    except Game.DoesNotExist:
        messages.error(request, 'Game not found')
        url = reverse('adminSchedule')
        return JsonResponse({'redirect': url})

