from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='teams/logos/', null=True, blank=True)
    stadium = models.CharField(max_length=100, blank=True, null=True)
    competitions = models.ManyToManyField('competition.Competition', related_name='teams')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    
    def get_upcoming_matches(self):
        return self.home_matches.filter(status='SCHEDULED').union(
            self.away_matches.filter(status='SCHEDULED')
        ).order_by('datetime')
    
    def get_past_matches(self):
        return self.home_matches.filter(status='FINISHED').union(
            self.away_matches.filter(status='FINISHED')
        ).order_by('-datetime')
    
    def get_live_matches(self):
        return self.home_matches.filter(status='LIVE').union(
            self.away_matches.filter(status='LIVE')
        )