from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('',views.matches_view,name='matches_view'),
    path('add_macth/',views.add_match_view,name='add_match_view'),
]
