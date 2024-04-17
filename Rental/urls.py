
from django.contrib import admin
from django.urls import path
from .views import signup, login, logout, get_neareast_locations, get_balance, add_balance,search_stations, give_feedback, get_estimated_cost, start_ride, end_ride, make_payment, get_payment_history

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
    path('search_stations/', search_stations, name='search_stations'),
    path('give_feedback/', give_feedback, name='give_feedback'),
    path('get_estimated_cost/', get_estimated_cost, name='get_estimated_cost'),
    path('start_ride/', start_ride, name='start_ride'),
    path('end_ride/', end_ride, name='end_ride'),
    path('make_payment/', make_payment, name='make_payment'),
    path('get_payment_history/', get_payment_history, name='get_payment_history'),


]
