# Celery Background Tasks Configuration
# football_project/celery.py
import os
from celery import Celery
from celery.schedules import crontab
from . import Competition, Standing  # Import Standing here

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_project.settings')

app = Celery('football_project')

# Use a string here so the worker doesn't serialize the object.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic task configuration
app.conf.beat_schedule = {
    'fetch-matches-every-6-hours': {
        'task': 'matches.tasks.fetch_matches',
        'schedule': crontab(hour='*/6'),
    },
    'fetch-standings-daily': {
        'task': 'competitions.tasks.fetch_standings',
        'schedule': crontab(hour=0, minute=30),  # Once a day
    },
    'update-live-matches-every-5-minutes': {
        'task': 'matches.tasks.update_live_matches',
        'schedule': crontab(minute='*/5'),
    },
    'fetch-team-logos': {
        'task': 'teams.tasks.fetch_team_logos',
        'schedule': crontab(hour=1),  # Once a day at 1 AM
    },
}

# matches/tasks.py
from celery import shared_task
import requests
from django.conf import settings
from . import Match, Competition, Team
from datetime import datetime, timedelta

@shared_task
def fetch_matches():
    """
    Fetch matches from Football API
    """
    headers = {
        'x-rapidapi-key': settings.API_FOOTBALL_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    # Fetch matches for previous week and next week
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now() + timedelta(days=7)
    
    params = {
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.get(
            f'{settings.API_BASE_URL}/fixtures', 
            headers=headers, 
            params=params
        )
        
        if response.status_code == 200:
            matches_data = response.json().get('response', [])
            
            for match_info in matches_data:
                # Extract match details
                fixture = match_info.get('fixture', {})
                teams = match_info.get('teams', {})
                goals = match_info.get('goals', {})
                
                # Find or create competition
                competition, _ = Competition.objects.get_or_create(
                    external_id=fixture.get('league', {}).get('id'),
                    defaults={
                        'name': fixture.get('league', {}).get('name'),
                        'country': fixture.get('league', {}).get('country'),
                        'type': 'league',  # Default, can be more specific
                        'current_season': fixture.get('league', {}).get('season', str(datetime.now().year))
                    }
                )
                
                # Find or create teams
                home_team, _ = Team.objects.get_or_create(
                    external_id=teams.get('home', {}).get('id'),
                    defaults={
                        'name': teams.get('home', {}).get('name'),
                        'logo': teams.get('home', {}).get('logo')
                    }
                )
                
                away_team, _ = Team.objects.get_or_create(
                    external_id=teams.get('away', {}).get('id'),
                    defaults={
                        'name': teams.get('away', {}).get('name'),
                        'logo': teams.get('away', {}).get('logo')
                    }
                )
                
                # Create or update match
                match, created = Match.objects.get_or_create(
                    external_id=fixture.get('id'),
                    defaults={
                        'competition': competition,
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': datetime.fromisoformat(fixture.get('date')),
                        'status': fixture.get('status', {}).get('short', 'upcoming').lower(),
                        'home_score': goals.get('home'),
                        'away_score': goals.get('away'),
                        'match_minute': fixture.get('status', {}).get('elapsed'),
                        'cup_round': fixture.get('league', {}).get('round')
                    }
                )
                
                # Update existing match if not created
                if not created:
                    match.home_score = goals.get('home')
                    match.away_score = goals.get('away')
                    match.status = fixture.get('status', {}).get('short', 'upcoming').lower()
                    match.match_minute = fixture.get('status', {}).get('elapsed')
                    match.save()

    except Exception as e:
        print(f"Error fetching matches: {e}")

@shared_task
def update_live_matches():
    """
    Update live match statuses and scores
    """
    headers = {
        'x-rapidapi-key': settings.API_FOOTBALL_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    
    # Fetch live matches
    try:
        response = requests.get(
            f'{settings.API_BASE_URL}/fixtures',
            headers=headers,
            params={'live': 'all'}
        )
        
        if response.status_code == 200:
            live_matches = response.json().get('response', [])
            
            for match_info in live_matches:
                fixture = match_info.get('fixture', {})
                goals = match_info.get('goals', {})
                
                # Update match if exists
                Match.objects.filter(external_id=fixture.get('id')).update(
                    status='live',
                    home_score=goals.get('home'),
                    away_score=goals.get('away'),
                    match_minute=fixture.get('status', {}).get('elapsed')
                )

    except Exception as e:
        print(f"Error updating live matches: {e}")

# competitions/tasks.py
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