from django.urls import path
from . import views


app_name='cric'
urlpatterns=[
    path('',views.home,name="home"),
    path('current-fixtures',views.index,name="index"),
    path('series/<int:series_id>/',views.seriesDisplay,name="series"),
    path('live-matches/',views.liveMatchesList,name="liveMatches"),
    path('series-list/',views.displaySeriesList,name="Series-List"),
    path('teams-list/',views.displayTeams,name="Teams-List"),
    path('series/<int:series_id>/teams-list/<int:team_id>/',views.TeamDisplay,name="Team"),

]
