from django.contrib import admin
from .models import Match, MatchEvent, LineUp, LineUpPlayer

class MatchEventInline(admin.TabularInline):
    model = MatchEvent
    extra = 0

class LineUpPlayerInline(admin.TabularInline):
    model = LineUpPlayer
    extra = 0

@admin.register(LineUp)
class LineUpAdmin(admin.ModelAdmin):
    inlines = [LineUpPlayerInline]
    list_display = ['match', 'team']
    list_filter = ['team']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [MatchEventInline]
    list_display = ['home_team', 'away_team', 'competition', 'datetime', 'status']
    list_filter = ['status', 'competition', 'datetime']
    search_fields = ['home_team__name', 'away_team__name']
    date_hierarchy = 'datetime'
    
    
    
    
    '''
    i want from you few things to edit . 
    about front-end i want all css code in one file and template dont have extra_css if possible with same design 
    also i want dark mode .
    
    for matches i dont want today and tommorow only i want to day and previus and next matches 
    if there many you do pagination in django 
    
    onle last thing the logo of the team dont apear api provide it ? if yes do it     

    
    '''