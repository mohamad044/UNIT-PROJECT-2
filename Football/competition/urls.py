from django.urls import path
from . import views

urlpatterns = [
    path('<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('', views.all_competitions, name='all_competitions'),
]