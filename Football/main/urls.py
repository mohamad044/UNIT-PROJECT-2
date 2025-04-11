from django.urls import path
from . import views

#app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('select-favorites/', views.select_favorites, name='select_favorites'),
    path('mode/',views.theme_mode_view,name='theme_mode_view')
]
