from django.shortcuts import render

# import api_view from djnago rest framework
from rest_framework.decorators import api_view
# import json response from django rest framework
from rest_framework.response import Response

# import jwt for token authentication
import jwt
from .models import User

# import mysql connector
from .sqlconnector import MySQLConnector

from .create_table_script import create_tables

# write a decorator to check if the user is authenticated
def is_authenticated(func):
    def wrapper(request, *args, **kwargs):
        # get the token from the request
        token = request.headers['Authorization']

        # remove bearer from the token
        token = token.split(' ')[1]

        # check if the token exists
        query = """
        SELECT * FROM User WHERE token = '{token}';"""
        query = query.format(token=token)
        conn = MySQLConnector()
        connection = conn.get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
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
    query = """
    SELECT * FROM User WHERE email = '{email}';"""
    query = query.format(email=data['email'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    if result:
        return Response({'error': 'User already exists'})

    # create a token
    token = jwt.encode({'name': data["username"]}, 'SECRET_KEY', algorithm='HS256')

    # create a user
    query = """
    INSERT INTO User (username, email, password, token) VALUES ('{username}', '{email}', '{password}', '{token}');"""
    query = query.format(username=data['username'], email=data['email'], password=data['password'], token=token)
    cursor.execute(query)
    connection.commit()
    conn.close_connection()


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
    # check if the user already exists
    query = """
        SELECT username,
        password,
        token
         FROM User WHERE email = '{email}';"""
    query = query.format(email=data['email'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    if not result:
        return Response({'error': 'User does not exist'})

    # check if the password is correct
    if data['password'] !=  result[0][1]:
        return Response({'error': 'Invalid password'})

    # create a token
    token = jwt.encode({'name': result[0][0]}, 'SECRET_KEY', algorithm='HS256')

    # save the token
    query = """
    UPDATE User SET token = '{token}' WHERE email = '{email}';"""
    query = query.format(token=token, email=data['email'])
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

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
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']
    # check if the token exists
    query = """
    SELECT * FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    if not result:
        return Response({'error': 'Invalid token'})

    # remove the token
    query = """
    UPDATE User SET token = '' WHERE token = '{token}';"""
    query = query.format(token=token)
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    # return the response
    return Response({'message': 'User logged out'})


@api_view(['GET'])
@is_authenticated
def get_all_users(request):

    # create a list of users
    data = {}
    data['status'] = "authenticated"
    return Response(data)


