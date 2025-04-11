from django.urls import path
from . import views

urlpatterns = [
    path('<int:team_id>/', views.team_detail, name='team_detail'),
]