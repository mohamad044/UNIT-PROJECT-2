import requests
import json
from datetime import datetime, timedelta

def get_football_data_api_football():
    url = "https://v3.football.api-sports.io/fixtures"
    
    params = {
        "league": "307",  # Saudi Pro League ID in API-Football
        "season": "2024"  # Current season
    }
    
    headers = {
        "x-rapidapi-key": "YOUR_API_KEY_HERE",  # You'll need to register
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def display_matches(data):
    if not data or 'response' not in data or len(data['response']) == 0:
        print("No matches found.")
        return
    
    print(f"\n===== SAUDI LEAGUE MATCHES ({len(data['response'])}) =====\n")
    
    for match in data['response']:
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
        status = match['fixture']['status']['long']
        
        score_home = match['goals']['home'] if match['goals']['home'] is not None else "-"
        score_away = match['goals']['away'] if match['goals']['away'] is not None else "-"
        
        print(f"Date: {match_date}")
        print(f"{home_team} {score_home} - {score_away} {away_team}")
        print(f"Status: {status}")
        print("-" * 40)

if __name__ == "__main__":
    football_data = get_football_data_api_football()
    if football_data:
        display_matches(football_data)
    else:
        print("Failed to retrieve football data")