import os
import django
import requests
from datetime import datetime, timedelta
import urllib.request

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Football.settings')
django.setup()

# Import your models
from competition.models import Competition, LeagueTable, LeagueTableEntry, CupStage
from team.models import Team
from match.models import Match, MatchEvent
from django.conf import settings

# API setup
API_KEY = settings.FOOTBALL_DATA_API_KEY  # Make sure this is set in your settings.py
BASE_URL = 'https://api.football-data.org/v4'
HEADERS = {'X-Auth-Token': API_KEY}

def fetch_competitions():
    """Fetch and save competitions"""
    print("Fetching competitions...")
    
    # Target competitions (Top 5 leagues + Saudi + major cups)
    target_competitions = [
        # Top 5 leagues
        {'id': 2021, 'name': 'Premier League', 'country': 'England', 'type': 'LEAGUE'},
        {'id': 2014, 'name': 'La Liga', 'country': 'Spain', 'type': 'LEAGUE'},
        {'id': 2019, 'name': 'Serie A', 'country': 'Italy', 'type': 'LEAGUE'},
        {'id': 2002, 'name': 'Bundesliga', 'country': 'Germany', 'type': 'LEAGUE'},
        {'id': 2015, 'name': 'Ligue 1', 'country': 'France', 'type': 'LEAGUE'},
        # Saudi League
        {'id': 2056, 'name': 'Saudi Pro League', 'country': 'Saudi Arabia', 'type': 'LEAGUE'},
        # Major cup competitions
        {'id': 2001, 'name': 'UEFA Champions League', 'country': 'Europe', 'type': 'CUP'},
    ]
    
    # Make sure the media directory exists
    os.makedirs('media/competitions/logos/', exist_ok=True)
    
    for comp_data in target_competitions:
        # Fetch additional info to get the crest URL
        response = requests.get(
            f"{BASE_URL}/competitions/{comp_data['id']}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            api_data = response.json()
            emblem_url = api_data.get('emblem')
            
            # Default competition data
            defaults = {
                'name': comp_data['name'],
                'country': comp_data['country'],
                'type': comp_data['type'],
            }
            
            # Download and save emblem if available
            if emblem_url:
                logo_path = f'competitions/logos/{comp_data["id"]}.png'
                full_path = os.path.join('media', logo_path)
                
                try:
                    urllib.request.urlretrieve(emblem_url, full_path)
                    defaults['logo'] = logo_path
                    print(f"Downloaded logo for {comp_data['name']}")
                except Exception as e:
                    print(f"Error downloading logo for {comp_data['name']}: {e}")
            
            competition, created = Competition.objects.update_or_create(
                id=comp_data['id'],
                defaults=defaults
            )
            
            if created:
                print(f"Created competition: {competition.name}")
            else:
                print(f"Updated competition: {competition.name}")
        else:
            print(f"Error fetching competition {comp_data['id']}: {response.status_code}")
    
    print(f"Total competitions: {Competition.objects.count()}")

def fetch_teams():
    """Fetch teams for each competition"""
    print("Fetching teams...")
    
    # Make sure the media directory exists
    os.makedirs('media/teams/logos/', exist_ok=True)
    
    for competition in Competition.objects.all():
        print(f"Fetching teams for {competition.name}...")
        
        try:
            # Get competition details with teams
            response = requests.get(
                f"{BASE_URL}/competitions/{competition.id}/teams",
                headers=HEADERS
            )
            
            if response.status_code != 200:
                print(f"Error fetching teams for {competition.name}: {response.status_code}")
                continue
                
            data = response.json()
            
            if 'teams' not in data:
                print(f"No teams found for {competition.name}")
                continue
                
            for team_data in data['teams']:
                # Get team data
                team_name = team_data['name']
                team_short_name = team_data.get('shortName', team_name[:3].upper())
                team_country = team_data.get('area', {}).get('name', 'Unknown')
                crest_url = team_data.get('crest')
                
                # Default team data
                defaults = {
                    'name': team_name,
                    'short_name': team_short_name,
                    'country': team_country,
                }
                
                # Download and save crest if available
                if crest_url:
                    logo_path = f'teams/logos/{team_data["id"]}.png'
                    full_path = os.path.join('media', logo_path)
                    
                    try:
                        urllib.request.urlretrieve(crest_url, full_path)
                        defaults['logo'] = logo_path
                        print(f"Downloaded logo for {team_name}")
                    except Exception as e:
                        print(f"Error downloading logo for {team_name}: {e}")
                
                team, created = Team.objects.update_or_create(
                    id=team_data['id'],
                    defaults=defaults
                )
                
                # Make sure team is associated with this competition
                if competition not in team.competitions.all():
                    team.competitions.add(competition)
                
                if created:
                    print(f"Created team: {team.name}")
                else:
                    print(f"Updated team: {team.name}")
        
        except Exception as e:
            print(f"Error processing teams for {competition.name}: {e}")
    
    print(f"Total teams: {Team.objects.count()}")

def fetch_matches():
    """Fetch matches for all competitions"""
    print("Fetching matches...")
    
    # Date range for matches (past week to next month)
    date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    for competition in Competition.objects.all():
        print(f"Fetching matches for {competition.name}...")
        
        try:
            # Get matches for this competition
            response = requests.get(
                f"{BASE_URL}/competitions/{competition.id}/matches",
                headers=HEADERS,
                params={
                    'dateFrom': date_from,
                    'dateTo': date_to
                }
            )
            
            if response.status_code != 200:
                print(f"Error fetching matches for {competition.name}: {response.status_code}")
                continue
                
            data = response.json()
            
            if 'matches' not in data:
                print(f"No matches found for {competition.name}")
                continue
                
            for match_data in data['matches']:
                # Get home and away teams
                try:
                    home_team = Team.objects.get(id=match_data['homeTeam']['id'])
                    away_team = Team.objects.get(id=match_data['awayTeam']['id'])
                except Team.DoesNotExist:
                    print(f"Skipping match, team not found: {match_data['homeTeam']['name']} vs {match_data['awayTeam']['name']}")
                    continue
                
                # Map status
                status_mapping = {
                    'SCHEDULED': 'SCHEDULED',
                    'LIVE': 'LIVE',
                    'IN_PLAY': 'LIVE',
                    'PAUSED': 'LIVE',
                    'FINISHED': 'FINISHED',
                    'POSTPONED': 'SCHEDULED',
                    'SUSPENDED': 'SCHEDULED',
                    'CANCELED': 'SCHEDULED',
                }
                status = status_mapping.get(match_data['status'], 'SCHEDULED')
                
                # Parse datetime
                match_datetime = datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00'))
                
                # Handle cup stage if applicable
                cup_stage = None
                if competition.type == 'CUP' and 'stage' in match_data:
                    stage_mapping = {
                        'GROUP_STAGE': ('GROUP', 1),
                        'LAST_16': ('R16', 2),
                        'QUARTER_FINALS': ('QF', 3),
                        'SEMI_FINALS': ('SF', 4),
                        'FINAL': ('F', 5),
                    }
                    
                    if match_data['stage'] in stage_mapping:
                        stage_name, order = stage_mapping[match_data['stage']]
                        cup_stage, _ = CupStage.objects.get_or_create(
                            competition=competition,
                            name=stage_name,
                            defaults={'order': order}
                        )
                
                # Create or update match
                match, created = Match.objects.update_or_create(
                    id=match_data['id'],
                    defaults={
                        'competition': competition,
                        'home_team': home_team,
                        'away_team': away_team,
                        'datetime': match_datetime,
                        'status': status,
                        'home_score': match_data.get('score', {}).get('fullTime', {}).get('home'),
                        'away_score': match_data.get('score', {}).get('fullTime', {}).get('away'),
                        'minute': match_data.get('minute', '') if status == 'LIVE' else None,
                        'cup_stage': cup_stage,
                    }
                )
                
                if created:
                    print(f"Created match: {home_team.name} vs {away_team.name}")
                else:
                    print(f"Updated match: {home_team.name} vs {away_team.name}")
        
        except Exception as e:
            print(f"Error processing matches for {competition.name}: {e}")
    
    print(f"Total matches: {Match.objects.count()}")

def fetch_league_tables():
    """Fetch league tables for league competitions"""
    print("Fetching league tables...")
    
    for competition in Competition.objects.filter(type='LEAGUE'):
        print(f"Fetching table for {competition.name}...")
        
        try:
            # Get standings for this league
            response = requests.get(
                f"{BASE_URL}/competitions/{competition.id}/standings",
                headers=HEADERS
            )
            
            if response.status_code != 200:
                print(f"Error fetching table for {competition.name}: {response.status_code}")
                continue
                
            data = response.json()
            
            if 'standings' not in data:
                print(f"No standings found for {competition.name}")
                continue
            
            # Find the total standings table
            table_data = None
            for standing in data['standings']:
                if standing['type'] == 'TOTAL':
                    table_data = standing
                    break
            
            if not table_data:
                print(f"No TOTAL standings found for {competition.name}")
                continue
            
            # Create or get the league table
            league_table, _ = LeagueTable.objects.get_or_create(competition=competition)
            
            # Clear existing entries
            league_table.entries.all().delete()
            
            # Create new entries
            for entry_data in table_data['table']:
                try:
                    team = Team.objects.get(id=entry_data['team']['id'])
                    
                    LeagueTableEntry.objects.create(
                        table=league_table,
                        team=team,
                        position=entry_data['position'],
                        played=entry_data['playedGames'],
                        won=entry_data['won'],
                        drawn=entry_data['draw'],
                        lost=entry_data['lost'],
                        goals_for=entry_data['goalsFor'],
                        goals_against=entry_data['goalsAgainst'],
                        goal_difference=entry_data['goalDifference'],
                        points=entry_data['points'],
                    )
                    
                    print(f"Added table entry for {team.name}")
                except Team.DoesNotExist:
                    print(f"Team with ID {entry_data['team']['id']} not found")
                    continue
        
        except Exception as e:
            print(f"Error processing table for {competition.name}: {e}")
    
    print("League tables updated successfully")

def fetch_all_data():
    """Fetch all data in sequence"""
    fetch_competitions()
    fetch_teams()
    fetch_matches()
    fetch_league_tables()
    print("All data fetched successfully!")

if __name__ == "__main__":
    # Check if API key is set
    if not API_KEY:
        print("ERROR: No Football Data API key found. Set FOOTBALL_DATA_API_KEY in settings.py")
    else:
        fetch_all_data()