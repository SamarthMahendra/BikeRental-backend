from django.contrib import admin
from django.urls import path
from Rental.views import signup, login, logout, get_neareast_locations

urlpatterns = [
    # sign up api
    path(r'signup/', signup, name='signup'),
    # login api
    path('login/', login, name='login'),
    # get all stocks api
    path('logout/', logout, name='login'),

    path('nearest/', get_neareast_locations, name='nearest')


]
