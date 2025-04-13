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
    
    # Get related matches (other matches from the same competition)
    related_matches = Match.objects.filter(
        competition=match.competition,
        status='SCHEDULED'
    ).exclude(id=match_id).order_by('datetime')[:5]
    
    context = {
        'match': match,
        'is_bookmarked': is_bookmarked,
        'events': match.events.all().order_by('minute'),
        'home_lineup': match.lineups.filter(team=match.home_team).first(),
        'away_lineup': match.lineups.filter(team=match.away_team).first(),
        'related_matches': related_matches,
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

    context = {
        'upcoming_matches': upcoming_matches,
        'live_matches': live_matches,
        'finished_matches': finished_matches,
    }
    
    return render(request, 'match/bookmarked.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Match, MatchNotification

@login_required
def set_match_notification(request, match_id):
    """Set up email notification for a match"""
    match = get_object_or_404(Match, id=match_id)
    
    if request.method == 'POST':
        minutes_before = request.POST.get('minutes_before')
        
        if minutes_before:
            minutes_before = int(minutes_before)
            
            notification, created = MatchNotification.objects.update_or_create(
                user=request.user,
                match=match,
                defaults={'minutes_before': minutes_before, 'is_sent': False}
            )
            
            if minutes_before == 0:
                send_match_notification_email(notification)
                notification.is_sent = True
                notification.save()
                messages.success(request, "Test notification sent to your email.")
            else:
                messages.success(request, f"You'll be notified {minutes_before} minutes before the match starts.")
        else:
            MatchNotification.objects.filter(user=request.user, match=match).delete()
            messages.info(request, "Match notification removed.")
            
    return redirect('match_detail', match_id=match.id)

def send_match_notification_email(notification):
    """Send email notification for a match"""
    match = notification.match
    user = notification.user
    
    subject = f"Match Reminder: {match.home_team.name} vs {match.away_team.name}"
    
    message = f"""
Hello {user.username},

This is a reminder for the upcoming match:

{match.home_team.name} vs {match.away_team.name}
Competition: {match.competition.name}
Date: {match.datetime.strftime('%d %B %Y')}
Time: {match.datetime.strftime('%H:%M')}

Enjoy the match!

"""
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )