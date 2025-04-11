import requests
import json
from datetime import datetime

def get_football_data():
    league_id = 2021
    month = 3 
    year = 2025
    url = f"https://api.football-data.org/v4/competitions/{league_id}/matches"
    
    headers = {
        "X-Auth-Token": "ec2876283a5743b783063d55e77ff97b"  
    }
    
    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        matches = response.json()['matches']
        
        filtered_matches = []
        for match in matches:
            match_date = match['utcDate']
            date_obj = datetime.strptime(match_date, '%Y-%m-%dT%H:%M:%SZ')
            
            if date_obj.month == month and date_obj.year == year:
                home_team = match.get('homeTeam', {}).get('name', 'N/A')
                away_team = match.get('awayTeam', {}).get('name', 'N/A')
                
                score_home = match.get('score', {}).get('fullTime', {}).get('homeTeam', 'N/A')
                score_away = match.get('score', {}).get('fullTime', {}).get('awayTeam', 'N/A')
                
                date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                filtered_matches.append(f"{home_team} vs {away_team} - {score_home}:{score_away} on {date}")
        
        if filtered_matches:
            for match in filtered_matches:
                print(match)
        else:
            print(f"No matches found for {month}/{year}.")
    else:
        print(f"Error {response.status_code}: Unable to fetch data.")

if __name__ == "__main__":
    football_data = get_football_data()
    if football_data:
        print("football_data: " , football_data)
    else:
        print("Failed to retrieve football data")
