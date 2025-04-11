from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Competition, LeagueTable, CupStage

@login_required
def competition_detail(request, competition_id):
    """View for a specific competition, showing matches and standings"""
    competition = get_object_or_404(Competition, id=competition_id)
    
    # Get matches for this competition
    all_matches = competition.matches.all()
    
    # Time ranges
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    # Filter matches by date and status
    live_matches = all_matches.filter(status='LIVE')
    today_matches = all_matches.filter(datetime__date=today, status='SCHEDULED').order_by('datetime')
    tomorrow_matches = all_matches.filter(datetime__date=tomorrow, status='SCHEDULED').order_by('datetime')
    yesterday_matches = all_matches.filter(datetime__date=yesterday, status='FINISHED').order_by('-datetime')
    upcoming_matches = all_matches.filter(
        status='SCHEDULED',
        datetime__date__gt=tomorrow
    ).order_by('datetime')[:20]
    past_matches = all_matches.filter(
        status='FINISHED',
        datetime__date__lt=yesterday
    ).order_by('-datetime')[:20]
    
    context = {
        'competition': competition,
        'live_matches': live_matches,
        'today_matches': today_matches,
        'tomorrow_matches': tomorrow_matches,
        'yesterday_matches': yesterday_matches,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches,
    }
    
    if competition.type == 'LEAGUE':
        # Add league table to context
        try:
            league_table = competition.league_table
            context['league_table'] = league_table
            context['table_entries'] = league_table.entries.all()
        except LeagueTable.DoesNotExist:
            pass
    else:
        # For cup competitions, add stages
        cup_stages = competition.cup_stages.all().order_by('-order')
        context['cup_stages'] = cup_stages
        
        # Get matches for each stage
        stage_matches = {}
        for stage in cup_stages:
            stage_matches[stage.id] = stage.matches.all().order_by('datetime')
        
        context['stage_matches'] = stage_matches
    
    return render(request, 'competition/competition_detail.html', context)

@login_required
def all_competitions(request):
    """List all available competitions"""
    leagues = Competition.objects.filter(type='LEAGUE').order_by('country', 'name')
    cups = Competition.objects.filter(type='CUP').order_by('country', 'name')
    
    context = {
        'leagues': leagues,
        'cups': cups,
    }
    
    return render(request, 'competition/all_competitions.html', context)