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


@api_view(['POST'])
@is_authenticated
def get_neareast_locations(request):
    # write doc string with desc and params and return type
    """
    This function is used to get the nearest locations

    Parameters:
    request: request object

    Returns:
    Response: response object (list of locations)
    """

    # get lat and long from the request
    data = request.data
    lat = data['lat']
    long = data['long']

    query = """
    SELECT * FROM Stations
    LEFT JOIN Bike ON Stations.id = Bike.station_id
    WHERE ( 6371 * acos( cos( radians({lat}) ) * cos( radians( lat ) ) * cos( radians( long ) - radians({long}) ) + sin( radians({lat}) ) * sin( radians( lat ) ) ) ) < 5;"""
    query = query.format(lat=lat, long=long)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)


# api to check if user has minimum balance of 10usd
@api_view(['GET'])
@is_authenticated
def check_balance(request):
    """
    This function is used to check the balance of the user
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # check the balance
    query = """
    SELECT balance FROM BikeCard WHERE user_id = {user_id};"""
    query = query.format(user_id=user_id)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    if result[0][0] < 10:
        return Response({'error': 'Insufficient balance'})
    return Response({'message': 'Sufficient balance'})


@api_view(['POST'])
@is_authenticated
def book_bike(request):
    """
    This function is used to book a bike
    """
    # get the data from the request
    data = request.data

    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # book the bike
    query = """
    INSERT INTO BookingSchedule (user_id, bike_id, start_time, end_time) VALUES ({user_id}, {bike_id}, '{start_time}', '{end_time}');"""
    query = query.format(user_id=user_id, bike_id=data['bike_id'], start_time=data['start_time'], end_time=data['end_time'])
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    # make the bike unavailable
    query = """
    UPDATE Bike SET is_available = FALSE WHERE id = {bike_id};"""
    query = query.format(bike_id=data['bike_id'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Bike booked successfully'})


@api_view(['POST'])
@is_authenticated
def end_ride(request):
    """
    This function is used to end a ride
    """
    # get the data from the request
    data = request.data

    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # end the ride
    query = """
    UPDATE BookingSchedule SET end_time = '{end_time}' WHERE user_id = {user_id} AND bike_id = {bike_id} AND end_time IS NULL;"""
    query = query.format(user_id=user_id, bike_id=data['bike_id'], end_time=data['end_time'])
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    # make the bike available
    query = """
    UPDATE Bike SET is_available = TRUE WHERE id = {bike_id};"""
    query = query.format(bike_id=data['bike_id'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    # calculate total amount based on time
    query = """
    SELECT rate FROM Rate WHERE bike_id = {bike_id};"""
    query = query.format(bike_id=data['bike_id'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    rate = result[0][0]
    conn.close_connection()

    # time = current time - start time
    start_time_query = """
    SELECT start_time FROM BookingSchedule WHERE user_id = {user_id} AND bike_id = {bike_id} AND end_time IS NULL;"""
    start_time_query = start_time_query.format(user_id=user_id, bike_id=data['bike_id'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()

    cursor.execute(start_time_query)
    result = cursor.fetchall()
    start_time = result[0][0]
    conn.close_connection()

    # calculate total amount
    total_amount = rate * (data['end_time'] - start_time)
    data['total_amount'] = total_amount
    # deduct the amount from the card
    query = """
    UPDATE BikeCard SET balance = balance - {total_amount} WHERE user_id = {user_id};"""
    query = query.format(total_amount=total_amount, user_id=user_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    data["amount_deducted"] = total_amount

    # save the payment history
    query = """
    INSERT INTO PaymentHistory (user_id, amount, start_time, end_time) VALUES ({user_id}, {total_amount}, '{start_time}', '{end_time}');"""
    query = query.format(user_id=user_id, total_amount=total_amount, start_time=start_time, end_time=data['end_time'])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    return Response({'message': 'Ride ended successfully'})


@api_view(['POST'])
@is_authenticated
def give_feedback(request):
    """
    This function is used to give feedback
    """
    # get the data from the request
    data = request.data

    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # give feedback
    query = """
    INSERT INTO Feedback (user_id, feedback) VALUES ({user_id}, '{feedback}');"""
    query = query.format(user_id=user_id, feedback=data['feedback'])
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Feedback given successfully'})


@api_view(['GET'])
@is_authenticated
def get_payment_history(request):
    """
    This function is used to get the payment history
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # get the payment history
    query = """
    SELECT * FROM PaymentHistory WHERE user_id = {user_id};"""
    query = query.format(user_id=user_id)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)



@api_view(['GET'])
@is_authenticated
def get_payment_history(request):
    """
    This function is used to get the payment history
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # get the payment history
    query = """
    SELECT * FROM PaymentHistory WHERE user_id = {user_id};"""
    query = query.format(user_id=user_id)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)


@api_view(['GET'])
@is_authenticated
def get_location_history(request):
    """
    This function is used to get the location history
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # get the location history
    query = """
    SELECT * FROM LocationHistory WHERE user_id = {user_id};"""
    query = query.format(user_id=user_id)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)


@api_view(['POST'])
@is_authenticated
def add_balance(request):
    """
    This function is used to add balance to the card
    """
    # get the data from the request
    data = request.data

    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # add balance
    query = """
    UPDATE BikeCard SET balance = balance + {amount} WHERE user_id = {user_id};"""
    query = query.format(amount=data['amount'], user_id=user_id)
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Balance added successfully'})


@api_view(['GET'])
@is_authenticated
def get_balance(request):
    """
    This function is used to get the balance
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # get the balance
    query = """
    SELECT balance FROM BikeCard WHERE user_id = {user_id};"""
    query = query.format(user_id=user_id)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result[0][0])



# Get Bike Details:
@api_view(['GET'])
@is_authenticated
def get_bike_details(request):
    """
    This function is used to get the bike details
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # get the bike details
    query = """
    SELECT * FROM Bike;"""
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)


# Search Stations
@api_view(['GET'])
@is_authenticated
def search_stations(request):
    """
    This function is used to search the stations
    """
    # get the user id from the token
    token = request.headers['Authorization']
    token = token.split(' ')[1]
    user_name = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])['name']

    # get the user id
    query = """
    SELECT id FROM User WHERE token = '{token}';"""
    query = query.format(token=token)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    user_id = result[0][0]

    # get the stations
    query = """
    SELECT * FROM Stations;"""
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)


