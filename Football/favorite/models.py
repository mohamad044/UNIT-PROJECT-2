from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_competitions = models.ManyToManyField('competition.Competition', blank=True, related_name='followed_by')
    favorite_teams = models.ManyToManyField('team.Team', blank=True, related_name='followed_by')
    bookmarked_matches = models.ManyToManyField('match.Match', blank=True, related_name='bookmarked_by')
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def get_favorite_matches(self):
        """Get matches of favorite teams and competitions"""
        from match.models import Match
        
        team_matches = Match.objects.filter(
            models.Q(home_team__in=self.favorite_teams.all()) | 
            models.Q(away_team__in=self.favorite_teams.all())
        )
        
        competition_matches = Match.objects.filter(
            competition__in=self.favorite_competitions.all()
        )
        
        return (team_matches | competition_matches).distinct()
    
    def get_favorite_upcoming_matches(self):
        
        print("--- in get_favorite_upcoming_matches --- ")
        print(self.get_favorite_matches().filter(status='SCHEDULED').order_by('datetime'))
        print('---end --- ')
        return self.get_favorite_matches().filter(status='SCHEDULED').order_by('datetime')
    
    def get_favorite_live_matches(self):
        return self.get_favorite_matches().filter(status='LIVE')
    
    def get_favorite_past_matches(self):
        return self.get_favorite_matches().filter(status='FINISHED').order_by('-datetime')