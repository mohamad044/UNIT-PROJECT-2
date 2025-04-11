from django.db import models

# Create your models here.


class League(models.Model):
    
    name = models.CharField(max_length=1024)
    len_clubs = models.SmallIntegerField(default=20)
    country = models.CharField(max_length=1024)
    

