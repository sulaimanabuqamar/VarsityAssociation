from django.urls import path
from football import views

urlpatterns = [
    path("", views.schedule, name="football-schedule"),
    path('login/', views.loginUser, name="football-login"),
    path("about/", views.about, name="football-about"),    
    path("terms/", views.terms, name="football-terms"),
    path("privacy/", views.privacy, name="football-privacy"),
    path("FAQs/", views.FAQs, name="football-FAQs"),
    path("schedule/admin", views.adminSchedule, name="football-adminSchedule"),
    path('team/code/verify', views.verifyTeamCode, name='football-verify-team-code'),
    path("teams/", views.teams, name="football-teams"),
    path("stats/", views.stats, name="football-stats"),
    path("add/team", views.add_team, name="football-add-team"),
    path("schedule/boxscore/<int:game_id>/", views.boxScore, name="football-boxscore"),
    path("schedule/admin/boxscore/<int:game_id>/",
         views.adminBoxScore, name="football-AdminBoxscore"),   
    path("stats/allstats", views.allStats, name="football-allstats"),   
    path('admin/save/score/<int:game_id>',
         views.saveScores, name='football-save-scores'),
    path('admin/stats/team/<int:team_id>', views.teamStats, name='football-team-stats'), 
     path('admin/stats/team/<int:team_id>', views.teamStats, name='football-team-stats'),
     path('select/gender/',views.selectGender,name='football-select-gender'),
       
]
