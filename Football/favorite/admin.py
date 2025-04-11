from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['favorite_competitions', 'favorite_teams', 'bookmarked_matches']