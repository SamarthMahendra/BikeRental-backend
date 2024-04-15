
from django.contrib import admin
from django.urls import path
from .views import signup, login, logout, get_neareast_locations, get_balance, add_balance,search_stations

urlpatterns = [
    # sign up api
    path(r'signup/', signup, name='signup'),
    # login api
    path('login/', login, name='login'),
    # get all stocks api
    path('logout/', logout, name='login'),
    # get stations
    path('get_nearby_stations/', get_neareast_locations, name='get_nearby_stations'),
    path('get_balance/', get_balance, name='get_balance'),
    path('add_balance/', add_balance, name='add_balance'),
    path('search_stations/', search_stations, name='search_stations')

]
