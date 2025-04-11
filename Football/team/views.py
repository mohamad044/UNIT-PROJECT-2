from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Team

@login_required
def team_detail(request, team_id):
    """View showing team details and matches"""
    team = get_object_or_404(Team, id=team_id)
    
    # Time ranges for organizing matches
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    # Get team's matches
    upcoming_matches = team.get_upcoming_matches()
    past_matches = team.get_past_matches()
    live_matches = team.get_live_matches()
    
    # Filter matches for specific dates
    today_matches = upcoming_matches.filter(datetime__date=today)
    tomorrow_matches = upcoming_matches.filter(datetime__date=tomorrow)
    yesterday_matches = past_matches.filter(datetime__date=yesterday)
    
    # Get all competitions this team plays in
    competitions = team.competitions.all()
    
    context = {
        'team': team,
        'live_matches': live_matches,
        'today_matches': today_matches,
        'tomorrow_matches': tomorrow_matches,
        'yesterday_matches': yesterday_matches,
        'upcoming_matches': upcoming_matches.exclude(datetime__date__in=[today, tomorrow])[:10],
        'past_matches': past_matches.exclude(datetime__date=yesterday)[:10],
        'competitions': competitions,
    }
    
    return render(request, 'team/team_detail.html', context)