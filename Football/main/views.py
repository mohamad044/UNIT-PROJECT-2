from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from match.models import Match
from favorite.models import UserProfile
from competition.models import Competition
from team.models import Team

@login_required
def home(request):
    """Home page showing matches based on user preferences with pagination"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    today = timezone.now().date()
    
    view_preference = request.GET.get('view', 'favorite')
    page_type = request.GET.get('page_type', 'today') 
    page = request.GET.get('page', 1)
    
    if page_type == 'previous':
        start_date = today - timedelta(days=30)
        end_date = today - timedelta(days=1)
        status = 'FINISHED'
        order = '-datetime'
    elif page_type == 'next':
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=30)
        status = 'SCHEDULED'
        order = 'datetime'
    else:  
        start_date = today
        end_date = today
        status = None  
        order = 'datetime'
    
    if view_preference == 'favorite':
        if status:
            favorite_matches = profile.get_favorite_matches().filter(
                status=status,
                datetime__date__range=[start_date, end_date]
            ).order_by(order)
        else:
            # For today's matches, include all statuses
            favorite_matches = profile.get_favorite_matches().filter(
                datetime__date=today
            ).order_by(order)
        
        matches_to_paginate = favorite_matches
        live_matches = profile.get_favorite_live_matches()
    else:
        # Get all matches
        if status:
            # For previous or next matches
            all_matches = Match.objects.filter(
                status=status,
                datetime__date__range=[start_date, end_date]
            ).order_by(order)
        else:
            # For today's matches, include all statuses
            all_matches = Match.objects.filter(
                datetime__date=today
            ).order_by(order)
        
        matches_to_paginate = all_matches
        live_matches = Match.objects.filter(status='LIVE')
    
    paginator = Paginator(matches_to_paginate, 6)  
    
    try:
        paginated_matches = paginator.page(page)
    except PageNotAnInteger:
        paginated_matches = paginator.page(1)
    except EmptyPage:
        paginated_matches = paginator.page(paginator.num_pages)
    
    context = {
        'matches': paginated_matches,
        'live_matches': live_matches,
        'view_preference': view_preference,
        'page_type': page_type,
    }
    
    return render(request, 'main/home.html', context)

@login_required
def select_favorites(request):
    """Page for selecting favorite competitions and teams"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        selected_competitions = request.POST.getlist('competitions')
        selected_teams = request.POST.getlist('teams')
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
                print(team.logo)
                profile.favorite_teams.add(team)
            except Team.DoesNotExist:
                continue
        
        return redirect('home')
    
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