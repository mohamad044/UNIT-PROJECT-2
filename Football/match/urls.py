from django.urls import path
from . import views

urlpatterns = [
    path('<int:match_id>/', views.match_detail, name='match_detail'),
    path('bookmarked/', views.bookmarked_matches, name='bookmarked_matches'),
    path('match/<int:match_id>/notify/', views.set_match_notification, name='set_match_notification'),
]