from django.db import models
from django.contrib.auth.models import User
class Match(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('FINISHED', 'Finished'),
    ]
    
    competition = models.ForeignKey('competition.Competition', on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey('team.Team', on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey('team.Team', on_delete=models.CASCADE, related_name='away_matches')
    datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    
    minute = models.CharField(max_length=10, null=True, blank=True)
    
    cup_stage = models.ForeignKey('competition.CupStage', on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='matches')
    
    class Meta:
        verbose_name_plural = 'Matches'
        ordering = ['datetime']
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.competition})"
    
    @property
    def is_finished(self):
        return self.status == 'FINISHED'
    
    @property
    def is_live(self):
        return self.status == 'LIVE'
    
    @property
    def winner(self):
        if not self.is_finished or self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None  # Draw


class MatchEvent(models.Model):
    EVENT_CHOICES = [
        ('GOAL', 'Goal'),
        ('OWN_GOAL', 'Own Goal'),
        ('YELLOW_CARD', 'Yellow Card'),
        ('RED_CARD', 'Red Card'),
        ('SUBSTITUTION', 'Substitution'),
        ('PENALTY_MISS', 'Penalty Miss'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    team = models.ForeignKey('team.Team', on_delete=models.CASCADE)
    minute = models.IntegerField()
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    player_name = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        ordering = ['minute']
    
    def __str__(self):
        return f"{self.minute}' - {self.get_event_type_display()} - {self.player_name}"


class LineUp(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='lineups')
    team = models.ForeignKey('team.Team', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Lineup: {self.team} - {self.match}"


class LineUpPlayer(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]
    
    lineup = models.ForeignKey(LineUp, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    is_starter = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.number} - {self.name}"
    
    


class MatchNotification(models.Model):
    """User notifications for upcoming matches"""
    NOTIFICATION_TIMES = [
        (5, '5 minutes before'),
        (15, '15 minutes before'),
        (30, '30 minutes before'),
        (60, '1 hour before'),
        (0, 'Test notification (send immediately)') 
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey('Match', on_delete=models.CASCADE)
    minutes_before = models.IntegerField(choices=NOTIFICATION_TIMES)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'match']
        
    def __str__(self):
        return f"Notification for {self.user.username} - {self.match} - {self.minutes_before} minutes before"