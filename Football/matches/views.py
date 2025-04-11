from django.shortcuts import render,redirect
from django.contrib import messages
from datetime import datetime
import requests
# Create your views here.
def add_match_view(request):
    if not request.user.is_staff:
        messages.success(request,"Only staff can access this page ", "alert-danger")
        return redirect('main:home_view')
    return render(request,'add_match.html')

def get_football_data():
    league_id = 2021
    month = 1 
    year = 2025
    url = f"https://api.football-data.org/v4/competitions/{league_id}/matches"
    
    headers = {
        "X-Auth-Token": "ec2876283a5743b783063d55e77ff97b"  # Replace with your actual API key
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matches = response.json()['matches']
        
        filtered_matches = []
        
        for index,match in enumerate(matches):
            game = dict(match)
            if index == 0:
                print("type: " , type(match))
                for m in match:
                    print(f"type:{type(m)}: {m}")
                    print(f"value({type(match[m])}): {match[m]}")
            match_date = match['utcDate']
            date_obj = datetime.strptime(match_date, '%Y-%m-%dT%H:%M:%SZ')
            
            if date_obj.month == month and date_obj.year == year:
                home_team = match.get('homeTeam', {}).get('name', 'N/A')
                away_team = match.get('awayTeam', {}).get('name', 'N/A')
                score_home = match.get('score', {}).get('fullTime', {}).get('home', 'NA')
                score_away = match.get('score', {}).get('fullTime', {}).get('away', 'NA')
                home_crest = match.get('homeTeam',{}).get('crest',{})
                away_crest = match.get('awayTeam',{}).get('crest',{})
                match_date = date_obj.strftime('%Y-%m-%d')
                match_time = date_obj.strftime("%H:%M")
                filtered_matches.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_crest':home_crest,
                    'away_crest':away_crest,
                    'score_home': score_home,
                    'score_away': score_away,
                    'match_date': match_date,
                    'match_time':match_time,
                })
        return filtered_matches
    else:
        return []


def matches_view(request):
    matches = get_football_data() 
    league = "Premiur League" 
    return render(request, 'matches.html', {'league':league ,'matches': matches})
