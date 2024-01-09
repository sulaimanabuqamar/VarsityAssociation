from django.urls import path
from basketball import views

urlpatterns = [
     path("about/", views.about, name="about"),    
     path("terms/", views.terms, name="terms"),
     path("privacy/", views.privacy, name="privacy"),
     path("FAQs/", views.FAQs, name="FAQs"),
     path("", views.schedule, name="schedule"),
     path("schedule/admin", views.adminSchedule, name="adminSchedule"),
     path('team/code/verify', views.verifyTeamCode, name='verify-team-code'),
     path("teams/", views.teams, name="teams"),
     path("stats/", views.stats, name="stats"),
     path("add/team", views.add_team, name="add-team"),
     path("schedule/boxscore/<int:game_id>/", views.boxScore, name="boxscore"),
     path("schedule/admin/boxscore/<int:game_id>/",
     views.adminBoxScore, name="AdminBoxscore"),
     # path("schedule/boxscore/<int:game_id>/save/", views.savePlayerStats, name="save_player_stats"),
     path("stats/allstats", views.allStats, name="allstats"),   
     path('admin/save/score/<int:game_id>',
     views.saveScores, name='save-scores'),
     path('admin/stats/team/<int:team_id>', views.teamStats, name='team-stats'),
     path('login/', views.loginUser, name="login"),
     path('select/gender/',views.selectGender,name='basketball-select-gender'),
]
