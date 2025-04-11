from django.shortcuts import render,redirect
from django.http import HttpRequest
# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from match.models import Match
from favorite.models import UserProfile
from competition.models import Competition
from team.models import Team

@login_required
def home(request):
    """Home page showing matches based on user preferences"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Time ranges
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    # Get matches based on view preference
    view_preference = request.GET.get('view', 'favorite')
    
    if view_preference == 'favorite':
        # Show matches based on user's favorites
        live_matches = profile.get_favorite_live_matches()
        today_matches = profile.get_favorite_upcoming_matches().filter(
            datetime__date=today
        ).order_by('datetime')
        #tomorrow_matches = profile.get_favorite_matches().filter(status='SCHEDULED').order_by('datetime')

        tomorrow_matches = profile.get_favorite_matches().filter(status='SCHEDULED').order_by('datetime')

        
        yesterday_matches = profile.get_favorite_past_matches().filter(
            datetime__date=yesterday
        ).order_by('-datetime')
    else:
        # Show all matches
        live_matches = Match.objects.filter(status='LIVE')
        today_matches = Match.objects.filter(
            status='SCHEDULED',
            datetime__date=today
        ).order_by('datetime')
        tomorrow_matches = Match.objects.filter(
            status='SCHEDULED',
            datetime__date=tomorrow
        ).order_by('datetime')
        yesterday_matches = Match.objects.filter(
            status='FINISHED',
            datetime__date=yesterday
        ).order_by('-datetime')
    
    context = {
        'live_matches': live_matches,
        'today_matches': today_matches,
        'tomorrow_matches': tomorrow_matches, 
        'yesterday_matches': yesterday_matches,
        'view_preference': view_preference,
    }
    
    return render(request, 'main/home.html', context)

@login_required
def select_favorites(request):
    """Page for selecting favorite competitions and teams"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission for saving favorites
        selected_competitions = request.POST.getlist('competitions')
        selected_teams = request.POST.getlist('teams')
        
        # Update user's favorites
        profile.favorite_competitions.clear()
        for comp_id in selected_competitions:
            try:
                competition = Competition.objects.get(id=comp_id)
                profile.favorite_competitions.add(competition)
            except Competition.DoesNotExist:
                continue
        
        profile.favorite_teams.clear()
        for team_id in selected_teams:
            try:
                team = Team.objects.get(id=team_id)
                profile.favorite_teams.add(team)
            except Team.DoesNotExist:
                continue
        
        return redirect('home')
    
    # Display form for selecting favorites
    competitions = Competition.objects.all().order_by('country', 'name')
    teams = Team.objects.all().order_by('name')
    
    context = {
        'competitions': competitions,
        'teams': teams,
        'selected_competitions': profile.favorite_competitions.all(),
        'selected_teams': profile.favorite_teams.all(),
    }
    
    return render(request, 'main/select_favorite.html', context)

def theme_mode_view(request:HttpRequest):
    referer = request.META.get('HTTP_REFERER', '/')
    response = redirect(referer)
    current_mode = request.COOKIES.get('dark_mode')
    
    if current_mode == 'true':
        response.set_cookie('dark_mode', 'false')
    else:
        response.set_cookie('dark_mode', 'true')
    return response