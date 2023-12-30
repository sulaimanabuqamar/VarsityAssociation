from django.urls import path
from volleyball import views

urlpatterns = [
    path("", views.schedule, name="volleyball-schedule"),
    path('login/', views.loginUser, name="volleyball-login"),
    path("about/", views.about, name="volleyball-about"),    
    path("terms/", views.terms, name="volleyball-terms"),
    path("privacy/", views.privacy, name="volleyball-privacy"),
    path("FAQs/", views.FAQs, name="volleyball-FAQs"),
    path("schedule/admin", views.adminSchedule, name="volleyball-adminSchedule"),
    path('team/code/verify', views.verifyTeamCode, name='volleyball-verify-team-code'),
    path("teams/", views.teams, name="volleyball-teams"),
    path("stats/", views.stats, name="volleyball-stats"),
    path("add/team", views.add_team, name="volleyball-add-team"),
    path("schedule/boxscore/<int:game_id>/", views.boxScore, name="volleyball-boxscore"),
    path("schedule/admin/boxscore/<int:game_id>/",
         views.adminBoxScore, name="volleyball-AdminBoxscore"), 
    path("schedule/admin/boxscore/<int:game_id>",
         views.adminBoxScore, name="volleyball-AdminBoxscore"), 
    path("stats/allstats", views.allStats, name="volleyball-allstats"),   
    path('admin/save/score/<int:game_id>/',
         views.saveScores, name='volleyball-save-scores'),
     path('admin/save/score/<int:game_id>/<int:set_id>/',
         views.saveScores, name='set-volleyball-save-scores'),
    path('admin/stats/team/<int:team_id>', views.teamStats, name='volleyball-team-stats'), 
     path('admin/stats/team/<int:team_id>', views.teamStats, name='volleyball-team-stats'),
       
]
