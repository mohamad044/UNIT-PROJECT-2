import requests
from datetime import datetime, timedelta
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class FootballDataAPI:
    BASE_URL = 'https://api.football-data.org/v4'
    
    def __init__(self):
        self.api_key = settings.FOOTBALL_DATA_API_KEY
        self.headers = {'X-Auth-Token': self.api_key}
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the API with error handling"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_competitions(self):
        """Get available competitions"""
        return self._make_request('competitions')
    
    def get_competition(self, competition_id):
        """Get details for a specific competition"""
        return self._make_request(f'competitions/{competition_id}')
    
    def get_competition_matches(self, competition_id, date_from=None, date_to=None):
        """Get matches for a competition with optional date filters"""
        params = {}
        if date_from:
            params['dateFrom'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['dateTo'] = date_to.strftime('%Y-%m-%d')
        
        return self._make_request(f'competitions/{competition_id}/matches', params)
    
    def get_competition_standings(self, competition_id):
        """Get current standings for a league competition"""
        return self._make_request(f'competitions/{competition_id}/standings')
    
    def get_team(self, team_id):
        """Get details for a specific team"""
        return self._make_request(f'teams/{team_id}')
    
    def get_team_matches(self, team_id, date_from=None, date_to=None):
        """Get matches for a team with optional date filters"""
        params = {}
        if date_from:
            params['dateFrom'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['dateTo'] = date_to.strftime('%Y-%m-%d')
        
        return self._make_request(f'teams/{team_id}/matches', params)
    
    def get_match(self, match_id):
        """Get details for a specific match"""
        return self._make_request(f'matches/{match_id}')
    
    def get_matches(self, date_from=None, date_to=None, status=None):
        """Get matches with optional filters"""
        params = {}
        if date_from:
            params['dateFrom'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['dateTo'] = date_to.strftime('%Y-%m-%d')
        if status:
            params['status'] = status
        
        return self._make_request('matches', params)
    
    def get_live_matches(self):
        """Get currently live matches"""
        return self._make_request('matches', {'status': 'LIVE'})
    
    def get_today_matches(self):
        """Get today's matches"""
        today = datetime.now().date()
        return self._make_request('matches', {
            'dateFrom': today.strftime('%Y-%m-%d'),
            'dateTo': today.strftime('%Y-%m-%d')
        })


# Helper functions for syncing data
def sync_competitions():
    """Sync competitions data from API to database"""
    from competition.models import Competition
    
    api = FootballDataAPI()
    competitions_data = api.get_competitions()
    
    if not competitions_data or 'competitions' not in competitions_data:
        logger.error("Failed to fetch competitions data")
        return
    
    # Focus on top 5 leagues + Saudi + major competitions
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
        {'id': 2018, 'name': 'European Championship', 'country': 'Europe', 'type': 'CUP'},
        {'id': 2000, 'name': 'FIFA World Cup', 'country': 'World', 'type': 'CUP'},
    ]
    
    for comp_data in target_competitions:
        competition, created = Competition.objects.update_or_create(
            id=comp_data['id'],
            defaults={
                'name': comp_data['name'],
                'country': comp_data['country'],
                'type': comp_data['type'],
            }
        )
        
        if created:
            logger.info(f"Created competition: {competition.name}")
        else:
            logger.info(f"Updated competition: {competition.name}")


def sync_teams(competition_id):
    """Sync teams for a specific competition"""
    from team.models import Team
    from competition.models import Competition
    
    try:
        competition = Competition.objects.get(id=competition_id)
    except Competition.DoesNotExist:
        logger.error(f"Competition with ID {competition_id} does not exist")
        return
    
    api = FootballDataAPI()
    standings_data = api.get_competition_standings(competition_id)
    
    if not standings_data or 'standings' not in standings_data:
        logger.error(f"Failed to fetch standings for competition {competition_id}")
        return
    
    # For league competitions
    if competition.type == 'LEAGUE':
        # Usually the first element is the overall table
        if standings_data['standings'][0]['type'] == 'TOTAL':
            table_data = standings_data['standings'][0]
            
            for team_data in table_data['table']:
                team, created = Team.objects.update_or_create(
                    id=team_data['team']['id'],
                    defaults={
                        'name': team_data['team']['name'],
                        'short_name': team_data['team']['shortName'],
                        'country': competition.country,  # Assuming team is from competition country
                    }
                )
                
                # Make sure team is associated with this competition
                if competition not in team.competitions.all():
                    team.competitions.add(competition)
                
                if created:
                    logger.info(f"Created team: {team.name}")
                else:
                    logger.info(f"Updated team: {team.name}")


def sync_matches(days_back=7, days_forward=30):
    """Sync matches for a date range around today"""
    from match.models import Match
    from team.models import Team
    from competition.models import Competition, CupStage
    
    date_from = datetime.now() - timedelta(days=days_back)
    date_to = datetime.now() + timedelta(days=days_forward)
    
    api = FootballDataAPI()
    matches_data = api.get_matches(date_from=date_from, date_to=date_to)
    
    if not matches_data or 'matches' not in matches_data:
        logger.error("Failed to fetch matches data")
        return
    
    for match_data in matches_data['matches']:
        # Skip if competition or teams don't exist in our database
        try:
            competition = Competition.objects.get(id=match_data['competition']['id'])
            home_team = Team.objects.get(id=match_data['homeTeam']['id'])
            away_team = Team.objects.get(id=match_data['awayTeam']['id'])
        except (Competition.DoesNotExist, Team.DoesNotExist):
            continue
        
        # Convert status to our format
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
                'datetime': datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00')),
                'status': status,
                'home_score': match_data.get('score', {}).get('fullTime', {}).get('home'),
                'away_score': match_data.get('score', {}).get('fullTime', {}).get('away'),
                'minute': match_data.get('minute') if status == 'LIVE' else None,
                'cup_stage': cup_stage,
            }
        )
        
        if created:
            logger.info(f"Created match: {match}")
        else:
            logger.info(f"Updated match: {match}")


def sync_live_matches():
    """Sync only currently live matches - to be run more frequently"""
    from match.models import Match
    from team.models import Team
    from competition.models import Competition
    
    api = FootballDataAPI()
    matches_data = api.get_live_matches()
    
    if not matches_data or 'matches' not in matches_data:
        logger.error("Failed to fetch live matches data")
        return
    
    for match_data in matches_data['matches']:
        try:
            match = Match.objects.get(id=match_data['id'])
            
            # Update match status and score
            match.status = 'LIVE'
            match.minute = match_data.get('minute', '')
            match.home_score = match_data.get('score', {}).get('fullTime', {}).get('home')
            match.away_score = match_data.get('score', {}).get('fullTime', {}).get('away')
            match.save()
            
            logger.info(f"Updated live match: {match}")
        except Match.DoesNotExist:
            # If match doesn't exist, we'll create it in the next full sync
            pass


def sync_league_tables():
    """Sync league tables for all league competitions"""
    from competition.models import Competition, LeagueTable, LeagueTableEntry
    from team.models import Team
    
    for competition in Competition.objects.filter(type='LEAGUE'):
        api = FootballDataAPI()
        standings_data = api.get_competition_standings(competition.id)
        
        if not standings_data or 'standings' not in standings_data:
            logger.error(f"Failed to fetch standings for competition {competition.id}")
            continue
        
        # Find the total standings (usually the first element)
        table_data = None
        for standing in standings_data['standings']:
            if standing['type'] == 'TOTAL':
                table_data = standing
                break
        
        if not table_data:
            logger.error(f"No TOTAL standings found for competition {competition.id}")
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
                
                logger.info(f"Updated table entry for {team.name} in {competition.name}")
            except Team.DoesNotExist:
                logger.warning(f"Team with ID {entry_data['team']['id']} not found")
                continue
