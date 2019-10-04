from django.http import Http404
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
import requests
import numpy as np
import time
import json
#from django.http import HttpResponse
#from django.template import loader

# Create your views here.

def live_series_matches(single_series,liveSeries_matches,matches):
    for j in matches:
        singleMatch_dict = {}
        if single_series['Series_Id'] == j['series_id']:
                singleMatch_dict['Match_Id'] = j['match_id']
                singleMatch_dict['State'] = j['header']['state_title']
                singleMatch_dict['Desc'] = j['header']['match_desc']
                singleMatch_dict['Details']='https://www.cricbuzz.com/cricket-scores/{0}'.format(j['match_id'])
                if j['header']['toss'] != '':
                    singleMatch_dict['Toss'] = j['header']['toss']
                singleMatch_dict['Team1'] = j['team1']['name']
                singleMatch_dict['Team1_Id'] = j['team1']['id']
                singleMatch_dict['Team2'] = j['team2']['name']
                singleMatch_dict['Team2_Id'] = j['team2']['id']
                singleMatch_dict['Status'] = j['header']['status']
                if j['header']['state'] == 'inprogress' or j['header']['state'] == 'rain':
                    if singleMatch_dict['Team1_Id'] == j['bat_team']['id']:
                        singleMatch_dict['Batting_Team']=singleMatch_dict['Team1']

                    else:
                        singleMatch_dict['Batting_Team'] = singleMatch_dict['Team2']
                    singleMatch_dict['Batting_Score'] = j['bat_team']['innings'][len(j['bat_team']['innings'])-1]['score']
                    singleMatch_dict['Batting_Wkts'] = j['bat_team']['innings'][len(j['bat_team']['innings'])-1]['wkts']
                    singleMatch_dict['Batting_Overs'] = j['bat_team']['innings'][len(j['bat_team']['innings'])-1]['overs']

                liveSeries_matches = np.append(liveSeries_matches, singleMatch_dict)
    return liveSeries_matches


url="http://mapps.cricbuzz.com/cbzios/match/livematches"
def get_live_matches():
    mat = requests.get(url).json()
    matches = mat['matches']
    series_list = np.array([])
    series_list = [x['series_id'] for x in matches]
    series_list = list(set(series_list))
    series_list.sort()
    series = np.array([])
    series_dict = {}
    for i in series_list:
        for j in matches:
            if i == j['series_id']:
                # series=np.append(series,[j['series_name']])
                series_dict['Series_Id'] = i
                series_dict['Series_Title'] = j['series_name']
                series = np.append(series, [series_dict.copy()])
                break

    for i in series:
        liveSeries_matches = np.array([])
        # liveSeries_matches=list(filter(lambda x:  x['series_id'] == i['Series_Id'] ,matches))
        liveSeries_matches = live_series_matches(i, liveSeries_matches, matches)
        i['Live_Matches'] = liveSeries_matches
    return series

def index(request):
    series_all=get_live_matches()
    return render(request,'cric/index.html',{'series_all':series_all})


def home(request):
    return render(request,'cric/home.html',{})

def setLive(current_matches):
    # print(type(current_matches))
    current_matches['Live_Matches']=list(filter(lambda x: x['State'] == "In Progress",current_matches['Live_Matches']))
    if len(current_matches['Live_Matches']) == 0:
        return False
    else:
        return True
def liveMatchesList(request):
    live_stream = get_live_matches()
    live_stream=list(filter(lambda x: setLive(x) == True,live_stream))

    if len(live_stream) == 0:
        return render(request,'cric/liveMatches.html',{'error': 'No Live Matches Right Now'})
    return render(request,'cric/liveMatches.html',{'live_stream':live_stream})

def seriesTeams(series_id):
    t_url="http://mapps.cricbuzz.com/cbzios/series/"+str(series_id)+"/teams"
    s_teams_data = requests.get(t_url).json()
    s_teams=s_teams_data['teams']
    s_teamsList=np.array([])
    for x in s_teams:
        team_data={}
        team_data['team_id']=x['id']
        team_data['Team_Name']=x['name']
        team_data['Series_Id']=series_id
        s_teamsList=np.append(s_teamsList,team_data)
    return s_teamsList

def seriesVenues(series_id):
    v_url = "http://mapps.cricbuzz.com/cbzios/series/" + str(series_id) + "/venues"
    s_venues_data = requests.get(v_url).json()
    s_venues = s_venues_data['venues']
    s_venuesList = np.array([])
    for x in s_venues:
        venue_data = {}
        venue_data['venue_id'] = x['id']
        venue_data['Venue_Name'] = x['name']
        venue_data['Venue_Location'] = x['location']
        venue_data['Venue_Country'] = x['country']
        venue_data['Venue_url'] = x['url'].replace('\\','')
        venue_data['Venue_img'] = x['img'].replace('\\','')
        s_venuesList = np.append(s_venuesList, venue_data)
    return s_venuesList

def seriesPointsTable(series_id):
    p_url="http://mapps.cricbuzz.com/cbzios/pointtable/" + str(series_id)
    s_points_data = requests.get(p_url).json()
    if len(s_points_data) == 0:
        return []
    s_point_group=s_points_data['group']
    s_point_group=list(s_point_group)
    s_point_group=s_point_group[0]
    s_points=s_points_data['group'][s_point_group]
    s_pointsList = np.array([])
    for x in s_points:
        points_dict={}
        points_dict['id'] = x['id']
        points_dict['Team'] = x['name']
        points_dict['played'] = x['p']
        points_dict['won'] = x['w']
        points_dict['lose'] = x['l']
        points_dict['tied'] = x['t']
        points_dict['nr'] = x['nr']
        points_dict['points'] = x['points']
        points_dict['nrr'] = x['nrr']
        s_pointsList = np.append(s_pointsList, points_dict)
    return s_pointsList

def checkHour(hr):
    if hr >= 12:
        dayState = 'PM'
        if hr > 12:
            hr = hr - 12

    else:
        dayState = "AM"
        if hr == 0:
            hr = 12
    return [dayState, hr]

def getdateTime(dt):
    dt=int(dt)
    hour = time.strftime('%H', time.localtime(dt))
    mint = time.strftime('%M', time.localtime(dt))

    hour = checkHour(int(hour))
    months=['January','February','March','April','May','June','July',
            'August','September','October','November','December']
    # matchDate = time.strftime('%m %d, %Y ', time.localtime(dt))
    day = time.strftime('%d', time.localtime(dt))
    month = time.strftime('%m', time.localtime(dt))
    year = time.strftime('%Y', time.localtime(dt))
    matchDate='{0} {1}, {2}'.format(months[int(month)],day,year)
    matchTime = '{0}:{1} {2}'.format(hour[1],mint,hour[0])
    return [matchDate,matchTime]


def seriesMatches(series_id):
    m_url = "http://mapps.cricbuzz.com/cbzios/series/" + str(series_id) + "/matches"
    s_matches_data = requests.get(m_url).json()
    s_matches=s_matches_data['matches']
    s_matchesList=np.array([])
    for x in s_matches:
        match_data={}
        match_data['Match_Id']=x['match_id']
        Date_Time=getdateTime(x['header']['start_time'])
        match_data['Match_Date']=Date_Time[0]
        match_data['Match_Time'] = Date_Time[1]
        match_data['Match_Desc']=x['header']['match_desc']
        match_data['Details']='https://www.cricbuzz.com/cricket-scores/{0}'.format(x['match_id'])
        match_data['Status']=x['header']['status']
        match_data['Venue_Name']=x['venue']['name']
        match_data['Venue_Location'] = x['venue']['location']
        match_data['Team1_Id']=x['team1']['id']
        match_data['Team1_Name'] = x['team1']['name']
        match_data['Team2_Id'] = x['team2']['id']
        match_data['Team2_Name'] = x['team2']['name']
        s_matchesList=np.append(s_matchesList,match_data)
    return s_matchesList
def seriesDisplay(request,series_id):
    series_url="http://mapps.cricbuzz.com/cbzios/series/" + str(series_id)
    series_data=requests.get(series_url).json()
    series_name=series_data['series']['name']
    s_teamsList  = seriesTeams(series_id)
    s_venuesList = seriesVenues(series_id)
    s_pointsList = seriesPointsTable(series_id)
    s_matchesList = seriesMatches(series_id)
    if len(s_pointsList) == 0:
        return render(request, 'cric/seriesPage.html', {'seriesName': series_name,'teams': s_teamsList,
                                                        'venues': s_venuesList,'matches': s_matchesList,
                                                        'points_error':'No Points Table Available'})
    return render(request,'cric/seriesPage.html',{'seriesName': series_name,'teams':s_teamsList,
                                                  'venues':s_venuesList,'matches': s_matchesList,
                                                  'pointsTable':s_pointsList})


def getSeriesList():
    s_list=requests.get(url).json()
    s_list=s_list['matches']
    # s_list=list(set(s_list))
    seriesList=np.array([])
    series_dict={
        'Series_Id': '2697',
        'Series_Name': 'ICC Cricket World Cup 2019'
    }
    seriesList=np.append(seriesList,series_dict)
    checkRepeat=[]
    for x in s_list:
        if x['series_id'] not in checkRepeat:
            series_dict={}
            series_dict['Series_Id']=x['series_id']
            series_dict['Series_Name']=x['series_name']
            checkRepeat.append(x['series_id'])
            seriesList=np.append(seriesList,series_dict)

    return seriesList

def displaySeriesList(request):
    seriesList=getSeriesList()
    return render(request, 'cric/seriesList.html', {'seriesList': seriesList})

def getTeams(teamsList,series_id):
    team_url="http://mapps.cricbuzz.com/cbzios/series/"+ series_id +"/teams"
    teams_list=requests.get(team_url).json()
    teams_list=teams_list['teams']
    for i in teams_list:
        team_data={}
        team_data['Team_Id']=i['id']
        team_data['Team_Name']=i['name']
        team_data['Team_Captain']=i['captain']
        team_data['Series_Id']=series_id
        teamsList=np.append(teamsList,team_data)
    return teamsList

def displayTeams(request):
    seriesList = getSeriesList()
    teamsList=np.array([])
    for x in seriesList:
        teamsList=getTeams(teamsList,x['Series_Id'])

    return render(request,'cric/teams-list.html',{'teamsList':teamsList})

def getTeam(team):
    cricTeam=np.array([])
    for x in team:
        player_data={}
        player_data['Id']=x['id']
        player_data['Name']=x['f_name']
        player_data['Age']=x['age']
        player_data['Role']=x['role']
        player_data['Style']=x['style']
        player_data['Link']='https://www.cricbuzz.com/profiles/{0}'.format(player_data['Id'])
        player_data['Pic_url'] = "https://i.cricketcb.com/stats/img/faceImages/{0}.jpg".format(x['id'])
        cricTeam=np.append(cricTeam,player_data)
    return cricTeam
def TeamDisplay(request,series_id,team_id):
    t_url="http://mapps.cricbuzz.com/cbzios/series/"+str(series_id)+"/teams/"+ str(team_id) +"/squads"
    team=requests.get(t_url).json()
    team=getTeam(team)
    tname_url = "http://mapps.cricbuzz.com/cbzios/series/"+ str(series_id)+"/teams/"+ str(team_id)
    teamName = requests.get(tname_url).json()
    teamName=teamName['team']['name']
    return render(request,'cric/TeamPage.html',{'TeamName':teamName,'team':team})


def MatchDisplay(request,match_id):
    match_url="http://mapps.cricbuzz.com/cbzios/match/" + str(match_id)
    match_data=requests.get(match_url).json()
    return render(request,'cric/MatchPage.html',{'Match':match_data})