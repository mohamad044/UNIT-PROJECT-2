from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns =[
    path('signup/',views.signup_view,name='signup_view'),
    path('login/',views.login_view,name='login_view'),
    path('logout/',views.logout_view,name='logout_view'),  
    path('vertify/',views.verify_view,name='verify_view')


]