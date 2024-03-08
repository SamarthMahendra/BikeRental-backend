from django.shortcuts import render

# import api_view from djnago rest framework
from rest_framework.decorators import api_view
# import json response from django rest framework
from rest_framework.response import Response

# import jwt for token authentication
import jwt
from .models import User

# write a decorator to check if the user is authenticated
def is_authenticated(func):
    def wrapper(request, *args, **kwargs):
        # get the token from the request
        token = request.headers['Authorization']

        # remove bearer from the token
        token = token.split(' ')[1]

        # check if the token exists
        user = User.objects.filter(token=token).first()
        if not user:
            return Response({'error': 'Invalid token'})

        return func(request, *args, **kwargs)
    return wrapper

@api_view(['POST'])
def signup(request):
    """
    This function is used to signup a user
    """

    # get the data from the request
    data = request.data

    # check if the user already exists
    user = User.objects.filter(email=data['email']).first()
    if user:
        return Response({'error': 'User already exists'})

    # create a user
    user = User.objects.create(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    # create a token
    token = jwt.encode({'id': user.id}, 'SECRET_KEY', algorithm='HS256')

    # save the token
    user.token = token
    user.save()

    # return the response
    return Response({'token': token})


@api_view(['POST'])
def login(request):
    """
    This function is used to login a user
    """

    # get the data from the request
    data = request.data

    # check if the user exists
    user = User.objects.filter(email=data['email']).first()
    if not user:
        return Response({'error': 'User does not exist'})

    # check if the password is correct
    if data['password'] != user.password:
        return Response({'error': 'Invalid password'})

    # create a token
    token = jwt.encode({'id': user.id}, 'SECRET_KEY', algorithm='HS256')

    # save the token
    user.token = token
    user.save()

    # return the response
    return Response({'token': token})


@api_view(['GET'])
def logout(request):
    """
    This function is used to logout a user
    """

    # get the token from the request
    token = request.headers['Authorization']

    # user id from the token

    # remove bearer from the token
    token = token.split(' ')[1]
    user_id = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['id']
    # check if the token exists
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({'error': 'Invalid token'})

    # remove the token
    user.token = ''
    user.save()

    # return the response
    return Response({'message': 'User logged out'})


@api_view(['GET'])
@is_authenticated
def get_all_users(request):
    """
    This function is used to get all users
    """

    # get all users
    users = User.objects.all()

    # create a list of users
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })

    # return the response
    return Response(data)


