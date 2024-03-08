
from django.contrib import admin
from django.urls import path
from .views import signup, login, logout, get_all_users

urlpatterns = [
    # sign up api
    path(r'signup/', signup, name='signup'),
    # login api
    path('login/', login, name='login'),
    # get all stocks api
    path('logout/', logout, name='login'),
    # get all users api
    path('get_users/', get_all_users, name='get_users'),

]
