from celery import shared_task
from team.models import Team
@shared_task
def fetch_team_logos():
    """
    Background task to fetch logos for teams without logos
    """
    teams_without_logo = Team.objects.filter(logo__isnull=True)
    for team in teams_without_logo:
        team.fetch_logo()
