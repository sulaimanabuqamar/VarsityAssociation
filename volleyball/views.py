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
            return redirect('volleyball-adminSchedule') 
        return redirect('volleyball-schedule')
    

    page_data=GenderLeagueType.objects.all()
    return render(request,'volleyball/select-gender.html',{'page_data':page_data})  



# used loginUser since login function is built function
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('volleyball-adminSchedule')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # login only staff
            if user.is_staff:
                login(request, user)
                return redirect('volleyball-adminSchedule')
            else:
                messages.error(
                    request, 'You are not staff')

        else:
            messages.error(
                request, 'Invalid login credentials. Please try again.')

    return render(request, 'volleyball/Login.html')

def about(request):
    return render(request, "volleyball/About.html", {'title': 'About Us'})


def privacy(request):
    return render(request, "volleyball/Privacy.html", {'title': 'Privacy'})


def terms(request):
    return render(request, "volleyball/Terms.html", {'title': 'Terms'})


def FAQs(request):
    return render(request, "volleyball/FAQs.html", {'title': 'FAQ'})

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
        month_name = item['month'].strftime('%B')
        
        # Fetch games for the current month
        month_games = games.filter(game_date__month=item['month'].strftime('%m'))
        
        # Include VolleyballSet information for each game
        games_per_month[month_name] ={}

        for game in month_games:
            first_set= VolleyballSet.objects.filter(game=game).order_by('set_number').first()
            games_per_month[month_name][game]=first_set

    return render(request, "volleyball/Schedule.html", {'games_per_month': games_per_month, 'title': 'Schedule'})


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
        
    grouped_months = games.annotate(month=TruncMonth('game_date')).values(
    'month').annotate(data_count=Count('game_id')).order_by('month')

    games_per_month = {}

    for item in grouped_months:
        month_name = item['month'].strftime('%B')
        
        # Fetch games for the current month
        month_games = games.filter(game_date__month=item['month'].strftime('%m'))
        
        # Include VolleyballSet information for each game
        games_per_month[month_name] ={}

        for game in month_games:
            first_set= VolleyballSet.objects.filter(game=game).order_by('set_number').first()
            games_per_month[month_name][game]=first_set
           
    return render(request, "volleyball/AdminSchedule.html", {'games_per_month': games_per_month, 'title': 'Admin Schedule'})


def teams(request):
    team_gender=request.session.get('team_gender')
    teams = Team.objects.filter(team_gender=team_gender).order_by('-wins', '-loses')
    return render(request, "volleyball/Teams.html", {'teams': teams, 'title': 'teams'})


def stats(request):
    team_gender=request.session.get('team_gender')
    kill_leaders = Player.objects.filter(team__team_gender=team_gender,kills__gt=0).order_by('-kills')[:5]
    dig_leaders = Player.objects.filter(team__team_gender=team_gender,
        digs__gt=0).order_by('-digs')[:5]
    block_leaders = Player.objects.filter(team__team_gender=team_gender,
        blocks__gt=0).order_by('-blocks')[:5]
    context = {
        'title': 'Stats',
        'kill_leaders': kill_leaders,
        'dig_leaders': dig_leaders,
        'block_leaders': block_leaders,
    }

    return render(request, "volleyball/Stats.html", context)


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

            # if players less  than 8  raise  form error
            if len(player_formset) < 6 or len(player_formset) > 12:
                team_form.add_error(
                    None, "You must add minimum of 6 players")
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
                    return redirect('volleyball-teams')
                else:
                    team_form.add_error(
                        None, "Team not added")
            messages.error(request, 'Please scroll down and correct error(s)')
    else:
        previous_url = request.META.get('HTTP_REFERER') or reverse('volleyball-teams')
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
    return render(request, 'volleyball/add-team.html', context)

def boxScore(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)      
            
        players1_performance_dict = {}
        players2_performance_dict = {}
        team1_players = Player.objects.filter(team=game.team_1) 
        team2_players = Player.objects.filter(team=game.team_2)  

        # if game has one set  
        if  game.sets ==1:
            count_sets=1
            volley_sets=VolleyballSet.objects.filter(game=game).order_by('set_number').first()
            for player1 in team1_players:
                player1_performance = PlayerPerformance.objects.filter(volleyball_set=volley_sets,player=player1).first()
                players1_performance_dict[player1] = player1_performance
            for player2 in team2_players:
                player2_performance = PlayerPerformance.objects.filter(volleyball_set=volley_sets,player=player2).first()
                players2_performance_dict[player2] = player2_performance  
                 #otherwise all   
        else:
            volley_sets = VolleyballSet.objects.filter(game=game).order_by('set_number')[:game.sets]            
            count_sets = volley_sets.count()
            for  volley_set in  volley_sets :
                players1_performance_dict[volley_set] = {}  # Initialize nested dictionary
                for player1 in team1_players:
                    player1_performance = PlayerPerformance.objects.filter(player=player1,volleyball_set=volley_set).first()
                    players1_performance_dict[volley_set][player1] = player1_performance
            
            for volley_set in volley_sets:            
                players2_performance_dict[volley_set] = {}  # Initialize nested dictionary
                for player2 in team2_players:
                    player2_performance = PlayerPerformance.objects.filter(player=player2,volleyball_set=volley_set).first()
                    players2_performance_dict[volley_set][player2] = player2_performance

         
                      
        context = {
            'players1_performance_dict': players1_performance_dict,
            'players2_performance_dict': players2_performance_dict,
            'game': game,
            'title': 'Boxscore',
            'sets':volley_sets,
            'count_sets':count_sets,
            'team_1_players':team1_players,
            'team_2_players':team2_players,
        }
        return render(request, "volleyball/Boxscore.html", context)

    except Game.DoesNotExist:
        messages.error(
            request, 'Game not found')
        return redirect('volleyball-boxscore')


@ custom_login_required
def adminBoxScore(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        # super user access any game
        if not request.user.is_superuser:
            keeper = ScoreKeeperGame.objects.filter(
                score_keeper__user=request.user, game=game)
            if not keeper:
                messages.error(
                    request, 'You are not allowed to edit .')
                return redirect('volleyball-adminSchedule')        
        players1_performance_dict = {}
        players2_performance_dict = {}
        team1_players = Player.objects.filter(team=game.team_1) 
        team2_players = Player.objects.filter(team=game.team_2)  

        # if game has one set  
        if  game.sets ==1:
            count_sets=1
            volley_sets=VolleyballSet.objects.filter(game=game).order_by('set_number').first()
            for player1 in team1_players:
                player1_performance = PlayerPerformance.objects.filter(volleyball_set=volley_sets,player=player1).first()
                players1_performance_dict[player1] = player1_performance
            for player2 in team2_players:
                player2_performance = PlayerPerformance.objects.filter(volleyball_set=volley_sets,player=player2).first()
                players2_performance_dict[player2] = player2_performance  
                 #otherwise all   
        else:
            volley_sets = VolleyballSet.objects.filter(game=game).order_by('set_number')[:game.sets]
            count_sets = volley_sets.count()
            for  volley_set in  volley_sets :
                players1_performance_dict[volley_set] = {}  # Initialize nested dictionary
                for player1 in team1_players:
                    player1_performance = PlayerPerformance.objects.filter(player=player1,volleyball_set=volley_set).first()
                    players1_performance_dict[volley_set][player1] = player1_performance
            
            for volley_set in volley_sets:            
                players2_performance_dict[volley_set] = {}  # Initialize nested dictionary
                for player2 in team2_players:
                    player2_performance = PlayerPerformance.objects.filter(player=player2,volleyball_set=volley_set).first()
                    players2_performance_dict[volley_set][player2] = player2_performance
           
        context = {
            'players1_performance_dict': players1_performance_dict,
            'players2_performance_dict': players2_performance_dict,
            'game': game,
            'title': 'Admin Boxscore',
            'sets':volley_sets,
            'count_sets':count_sets,
            'team_1_players':team1_players,
            'team_2_players':team2_players,
        }
        return render(request, "volleyball/AdminBoxscore.html", context)

    except Game.DoesNotExist:
        messages.error(
            request, 'Game not found')
        return redirect('volleyball-adminSchedule')
    


def allStats(request):
    team_gender=request.session.get('team_gender')
    players = Player.objects.filter(team__team_gender=team_gender).order_by('-service_aces','-kills')
    return render(request, "volleyball/AllStats.html", {'players': players, 'title': 'All Stats'})


def teamStats(request, team_id):
    try:
        team = Team.objects.get(pk=team_id)
        players = Player.objects.filter(team=team)
        context = {'players': players,
                   'title': team.team_name + ' Players stats',
                   'team': team
                   }
        return render(request, "volleyball/team-stats.html", context)
    except Team.DoesNotExist:
        messages.error(
            request, 'Team not found')
        return redirect('volleyball-teams')


@ custom_login_required
@ require_POST
def saveScores(request,game_id, set_id=None):
    try:
        #  handle DoesNotExist automatically       
        game = Game.objects.get(pk=game_id)
        
        # Only superuser or authorized scorekeepers are allowed
        if not (request.user.is_superuser or ScoreKeeperGame.objects.filter(
                score_keeper__user=request.user, game=game).exists()):
            url = reverse('volleyball-adminSchedule')
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
   
        volley_set=VolleyballSet.objects.get(pk=set_id)
        # Get user and input field
        player_id = request.POST.get('player_id')
        input_value = request.POST.get('input_value')
        input_value = input_value if input_value.isdigit() else None
        column = request.POST.get('column')
        allowed_columns = [ 'attack_attempts','kills','errors','digs', 'blocks', 'solo_blocks_and_assisted_blocks', 'service_aces',]
   
        # Reject if column is not in allowed columns
        if column not in allowed_columns:
            return JsonResponse({'error': 'wrong field'})
       
        
        player = Player.objects.filter(player_id=player_id).first()
         
        if not player:
            return JsonResponse({'error': 'player not found'})

        if player.team not in [ volley_set.game.team_1, volley_set.game.team_2]:
            return JsonResponse({'error': 'player not found in that game'})

        # Create performance for players if it does not exist
        if not PlayerPerformance.objects.filter(volleyball_set=volley_set, player=player).exists():
            team_1_players = Player.objects.filter(team=game.team_1)
            team_2_players = Player.objects.filter(team=game.team_2)

            for team_player in team_1_players:
                PlayerPerformance.objects.get_or_create(volleyball_set=volley_set, player=team_player)

            for team_player in team_2_players:
                PlayerPerformance.objects.get_or_create(volleyball_set=volley_set, player=team_player)

        performance = PlayerPerformance.objects.get(volleyball_set=volley_set, player=player)
        setattr(performance, column, input_value)
        performance.save()        
        game = Game.objects.get(pk=volley_set.game.game_id)
        json_game=json.loads(serialize('json', [game]))[0]['fields']

        volley_sets= VolleyballSet.objects.filter(game=game).values()

        # Return all performances for the game to update if there is a change made in another user or tab
        player_performances = PlayerPerformance.objects.filter(
           volleyball_set=volley_set).values('attack_attempts','kills','errors','digs','blocks', 'solo_blocks_and_assisted_blocks','service_aces',)
        return JsonResponse({'success': 'Score Updated successfully', 'player_peformances': list(player_performances), 'volley_sets':list(volley_sets),'game':json_game})

    except Game.DoesNotExist:
        messages.error(request, 'Game not found')
        url = reverse('volleyball-adminSchedule')
        return JsonResponse({'redirect': url})
    except VolleyballSet.DoesNotExist:
        messages.error(request, 'Set not found')
        url = reverse('volleyball-adminSchedule')
        return JsonResponse({'redirect': url})
