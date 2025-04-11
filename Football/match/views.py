from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Match
from favorite.models import UserProfile

@login_required
def match_detail(request, match_id):
    """Detail view for a single match"""
    match = get_object_or_404(Match, id=match_id)
    profile = UserProfile.objects.get(user=request.user)
    
    # Check if match is bookmarked by user
    is_bookmarked = profile.bookmarked_matches.filter(id=match_id).exists()
    
    # Toggle bookmark status if requested
    if request.method == 'POST' and 'toggle_bookmark' in request.POST:
        if is_bookmarked:
            profile.bookmarked_matches.remove(match)
            is_bookmarked = False
        else:
            profile.bookmarked_matches.add(match)
            is_bookmarked = True
        
        # Redirect to remove the POST data (to prevent duplicate submissions)
        return redirect('match_detail', match_id=match_id)
    
    context = {
        'match': match,
        'is_bookmarked': is_bookmarked,
        'events': match.events.all().order_by('minute'),
        'home_lineup': match.lineups.filter(team=match.home_team).first(),
        'away_lineup': match.lineups.filter(team=match.away_team).first(),
    }
    
    return render(request, 'match/match_detail.html', context)

@login_required
def bookmarked_matches(request):
    """View showing all bookmarked matches"""
    profile = UserProfile.objects.get(user=request.user)
    
    # Get the bookmarked matches
    bookmarked = profile.bookmarked_matches.all().order_by('datetime')
    
    # Split into upcoming, live, and finished
    upcoming_matches = bookmarked.filter(status='SCHEDULED')
    live_matches = bookmarked.filter(status='LIVE')
    finished_matches = bookmarked.filter(status='FINISHED')
    related_matches = None #Match.competition.matches.filter(status='SCHEDULED')[:5]

    context = {
        'upcoming_matches': upcoming_matches,
        'live_matches': live_matches,
        'finished_matches': finished_matches,
        'related_matches' : related_matches,
    }
    
    return render(request, 'match/bookmarked.html', context)