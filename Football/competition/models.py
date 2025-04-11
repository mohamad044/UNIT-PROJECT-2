from django.db import models

class Competition(models.Model):
    COMPETITION_TYPE_CHOICES = [
        ('LEAGUE', 'League'),
        ('CUP', 'Cup'),
    ]
    
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=COMPETITION_TYPE_CHOICES)
    logo = models.ImageField(upload_to='competitions/logos/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.country})"
    
    class Meta:
        ordering = ['country', 'name']

class LeagueTable(models.Model):
    competition = models.OneToOneField(Competition, on_delete=models.CASCADE, related_name='league_table')
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Table for {self.competition.name}"

class LeagueTableEntry(models.Model):
    table = models.ForeignKey('LeagueTable', on_delete=models.CASCADE, related_name='entries')
    team = models.ForeignKey('team.Team', on_delete=models.CASCADE)
    position = models.IntegerField()
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        
    def __str__(self):
        return f"{self.position}. {self.team.name}"

class CupStage(models.Model):
    STAGE_CHOICES = [
        ('GROUP', 'Group Stage'),
        ('R16', 'Round of 16'),
        ('QF', 'Quarter-finals'),
        ('SF', 'Semi-finals'),
        ('F', 'Final'),
    ]
    
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='cup_stages')
    name = models.CharField(max_length=20, choices=STAGE_CHOICES)
    order = models.IntegerField()  # For sorting stages in correct order

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.competition.name} - {self.get_name_display()}"