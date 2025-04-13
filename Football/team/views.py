from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from . models import Team
from match.models import Match

@login_required
def team_detail(request, team_id):
    """View showing team details and matches"""
    team = get_object_or_404(Team, id=team_id)
    
    today = timezone.now().date()

    home_today = Match.objects.filter(
        datetime__date=today,
        home_team=team
    )
    away_today = Match.objects.filter(
        datetime__date=today,
        away_team=team
    )
    today_matches = list(home_today) + list(away_today)
    
    home_upcoming = Match.objects.filter(
        status='SCHEDULED',
        datetime__date__gt=today,
        home_team=team
    ).order_by('datetime')[:10]
    away_upcoming = Match.objects.filter(
        status='SCHEDULED',
        datetime__date__gt=today,
        away_team=team
    ).order_by('datetime')[:10]
    upcoming_matches = list(home_upcoming) + list(away_upcoming)
    
    home_past = Match.objects.filter(
        status='FINISHED',
        home_team=team
    ).order_by('-datetime')[:10]
    away_past = Match.objects.filter(
        status='FINISHED',
        away_team=team
    ).order_by('-datetime')[:10]
    past_matches = list(home_past) + list(away_past)
    
    home_live = Match.objects.filter(
        status='LIVE',
        home_team=team
    )
    away_live = Match.objects.filter(
        status='LIVE',
        away_team=team
    )
    live_matches = list(home_live) + list(away_live)
    
    context = {
        'team': team,
        'today_matches': today_matches,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
        'live_matches': live_matches,
        'competitions': team.competitions.all(),
    }
    
    return render(request, 'team/team_detail.html', context)