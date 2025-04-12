# competitions/tasks.py
from celery import shared_task
import requests
from django.conf import settings
from datetime import datetime
from .models import Competition, Standing
from team.models import Team

@shared_task
def fetch_standings():
    """
    Fetch league standings from Football API
    """
    headers = {
        'x-rapidapi-key': settings.API_FOOTBALL_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    # Fetch standings for top leagues
    top_leagues = [
        39,  # Premier League
        140,  # La Liga
        78,  # Bundesliga
        135,  # Serie A
        61,  # Ligue 1
        307,  # Saudi League
    ]
    
    for league_id in top_leagues:
        try:
            response = requests.get(
                f'{settings.API_BASE_URL}/standings',
                headers=headers,
                params={'league': league_id, 'season': datetime.now().year}
            )
            
            if response.status_code == 200:
                standings_data = response.json().get('response', [])
                
                for league_standings in standings_data:
                    competition, _ = Competition.objects.get_or_create(
                        external_id=league_id,
                        defaults={
                            'name': league_standings.get('league', {}).get('name'),
                            'type': 'league',
                            'current_season': str(datetime.now().year)
                        }
                    )
                    
                    # Clear existing standings for this competition
                    Standing.objects.filter(competition=competition).delete()
                    
                    # Process each team's standing
                    for team_standing in league_standings.get('league', {}).get('standings', [])[0]:
                        team, _ = Team.objects.get_or_create(
                            external_id=team_standing.get('team', {}).get('id'),
                            defaults={
                                'name': team_standing.get('team', {}).get('name'),
                                'logo': team_standing.get('team', {}).get('logo')
                            }
                        )
                        
                        Standing.objects.create(
                            competition=competition,
                            team=team,
                            position=team_standing.get('rank'),
                            played=team_standing.get('all', {}).get('played'),
                            won=team_standing.get('all', {}).get('win'),
                            drawn=team_standing.get('all', {}).get('draw'),
                            lost=team_standing.get('all', {}).get('lose'),
                            goals_for=team_standing.get('all', {}).get('goals', {}).get('for'),
                            goals_against=team_standing.get('all', {}).get('goals', {}).get('against'),
                            goal_difference=team_standing.get('goalsDiff'),
                            points=team_standing.get('points')
                        )
        
        except Exception as e:
            print(f"Error fetching standings for league {league_id}: {e}")