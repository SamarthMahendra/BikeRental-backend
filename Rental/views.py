import datetime

from django.shortcuts import render

# import api_view from djnago rest framework
from rest_framework.decorators import api_view
# import json response from django rest framework
from rest_framework.response import Response
  
# import jwt for token authentication
import jwt
from .models import User

# import mysql connector
from .sqlconnector import MySQLConnector, get_cursor

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
        conn.close_connection()

        if not result:
            return Response({'error': 'Invalid token'})

        # # append user id to the request and user_name
        request.user_id = result[0][0]
        request.user_name = result[0][1]
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

    query = """
    INSERT INTO BikeCard (Balance, UserID) VALUES (0, {user_id});"""
    query = query.format(user_id=result[0][0])
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
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
SELECT
    s.StationID,
    s.StationName,
    s.Address,
    s.Locatiion_lat AS Station_lat,
    s.Locatiion_lon AS Station_lon,
    JSON_ARRAYAGG(
        JSON_OBJECT(
            'bikeID', ab.BikeID,
            'range', ab.Bike_range,
            'last maintenance', ab.LastMaintenanceDate
        )
    ) AS available_bikes,
    (6371 * acos(cos(radians({lat})) * cos(radians(s.Locatiion_lat)) * cos(radians(s.Locatiion_lon) - radians({long})) + sin(radians({lat})) * sin(radians(s.Locatiion_lat)))) AS Distance
FROM
    stations s
LEFT JOIN (
    SELECT
        s.StationID,
        b.BikeID,
        IFNULL(e.Bike_range, -1) AS Bike_range,
        b.LastMaintenanceDate
    FROM
        stations s
    LEFT JOIN
        bike b ON s.StationID = b.StationID AND b.InUse = 0 AND b.status = 'Available'
    LEFT JOIN
        ebike e ON b.BikeID = e.BikeID
) AS ab ON s.StationID = ab.StationID
GROUP BY
    s.StationID, s.StationName, s.Address, s.Locatiion_lat, s.Locatiion_lon
ORDER BY
    Distance;
"""
    query = query.format(lat=lat, long=long)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    # reformat response
    response = {}

    stations = []
    for row in result:
        station = {
            "name": row[1],
            "StationID": row[0],
            "Address": row[2],
            "available_bikes": eval(row[5]),
            "lat": row[3],
            "lon": row[4],
            "distance_factor": row[6]
        }
        stations.append(station)
    response["stations"]= stations

    conn.close_connection()
    return Response(response)


# search stations
@api_view(['POST'])  # Use POST since we are submitting data
@is_authenticated
def search_stations(request):
    """
    Search for station locations based on a user-provided search keyword.

    Parameters:
    request (Request): The HTTP request object containing 'search_key' in the JSON body, which is used to filter station names.

    Returns:
    Response: A Django Rest Framework response object containing a filtered list of stations based on the search keyword.
    """
    # Extract the search keyword from the request data
    data = request.data
    search_key = data.get('search_key', '')  # Default to empty string if not provided

    # SQL query to fetch stations filtered by search keyword
    query = """
    SELECT
        s.StationID,
        s.StationName,
        s.Address,
        s.Locatiion_lat AS Station_lat,
        s.Locatiion_lon AS Station_lon,
        JSON_ARRAYAGG(
            JSON_OBJECT(
                'bikeID', ab.BikeID,
                'range', ab.Bike_range,
                'last maintenance', ab.LastMaintenanceDate
            )
        ) AS available_bikes
    FROM
        stations s
    LEFT JOIN (
        SELECT
            b.StationID,
            b.BikeID,
            IFNULL(e.Bike_range, -1) AS Bike_range,
            b.LastMaintenanceDate
        FROM
            bike b
        LEFT JOIN
            ebike e ON b.BikeID = e.BikeID
        WHERE
            b.InUse = 0 AND b.status = 'Available'
    ) AS ab ON s.StationID = ab.StationID
    WHERE
        s.StationName LIKE %s
    GROUP BY
        s.StationID, s.StationName, s.Address, s.Locatiion_lat, s.Locatiion_lon
    """

    # Connect to the database and execute the query
    conn = MySQLConnector()  # Assuming MySQLConnector is a class handling DB connections
    connection = conn.get_connection()
    cursor = connection.cursor()
    like_search_key = f"%{search_key}%"  # Format search key for SQL LIKE query
    cursor.execute(query, (like_search_key,))
    result = cursor.fetchall()

    # Format the response
    response = {}
    stations = []
    for row in result:
        station = {
            "StationID": row[0],
            "name": row[1],
            "Address": row[2],
            "lat": row[3],
            "lon": row[4],
            "available_bikes": eval(row[5])  # Assuming the data is returned as a JSON string
        }
        stations.append(station)
    response["stations"] = stations

    conn.close_connection()
    return Response(response)


# check balance
@api_view(['GET'])
@is_authenticated
def get_balance(request):
    """
    This function is used to check the balance of the user
    """
    user_id = request.user_id
    query = """
    SELECT balance FROM BikeCard WHERE UserID = {user_id};"""
    query = query.format(user_id=user_id)
    cursor, conn, _ = get_cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    res = {
        "balance": result[0][0]
    }
    return Response(res)

# add balance to card post request
@api_view(['POST'])
@is_authenticated
def add_balance(request):
    """
    This function is used to add balance to the card
    """
    user_id = request.user_id
    data = request.data
    query = """
    UPDATE BikeCard SET balance = balance + {amount} WHERE UserID = {user_id};"""
    query = query.format(amount=data['amount'], user_id=user_id)
    cursor, conn, connection = get_cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Balance added successfully'})



# start ride
# end ride
#
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

    user_name = request.user_name
    user_id = request.user_id

    start_station_id = data['station_id']
    end_station_id = data['end_station_id']
    bikeID = data['bike_id']
    feedback = data['feedback']

    # timestamp = current time
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rating = data['rating']


    cursor, conn, connection = get_cursor()
    query = """
    INSERT INTO Feedback (Rating, Comments, UserID, BikeID, Timestamp, StartStationID, EndStationID) VALUES ({rating}, '{feedback}', {user_id}, {bike_id}, '{timestamp}', {start_station_id}, {end_station_id});"""
    query = query.format(rating=rating, feedback=feedback, user_id=user_id, bike_id=bikeID, timestamp=timestamp, start_station_id=start_station_id, end_station_id=end_station_id)
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    your_feedback = {
        "rating": rating,
        "comments": feedback,
        "timestamp": timestamp
    }
    return Response({'message': 'Feedback given successfully','data':your_feedback})


@api_view(['GET'])
@is_authenticated
def get_payment_history(request):
    """
    This function is used to get the payment history
    """

    # get the user id
    user_id = request.user_id
    cursor , conn, connection = get_cursor()
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



# API to move a bike to maintenance
@api_view(['POST'])
@is_authenticated
def move_to_maintenance(request):
    """
    This function is used to move a bike to maintenance
    """
    # get the data from the request
    data = request.data

    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()

    # move the bike to maintenance
    query = """
    INSERT INTO MaintenanceRecord (DateOfMaintenance, Details, BikeID) VALUES ('{date_of_maintenance}', '{details}', {bike_id});"""
    query = query.format(date_of_maintenance=data['date_of_maintenance'], details=data['details'], bike_id=data['bike_id'])
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Bike moved to maintenance successfully'})


# API to get the maintenance Records with option to filter by bike id, date of maintenance
@api_view(['POST'])
@is_authenticated
def get_maintenance_records(request):
    """
    This function is used to get the maintenance records
    """
    # get the data from the request
    data = request.data

    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()

    # get the maintenance records
     # based on filers sent in the request
    query = """
    SELECT * FROM MaintenanceRecord WHERE 1=1 """
    if 'bike_id' in data:
        query += " AND BikeID = {bike_id}".format(bike_id=data['bike_id'])
    if 'date_of_maintenance' in data:
        query += " AND DateOfMaintenance = '{date_of_maintenance}'".format(date_of_maintenance=data['date_of_maintenance'])
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()
    return Response(result)

# remove bike from maintenance
@api_view(['POST'])
@is_authenticated
def remove_from_maintenance(request):
    """
    This function is used to remove a bike from maintenance
    """
    # get the data from the request
    data = request.data

    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()

    # remove the bike from maintenance
    query = """
    DELETE FROM MaintenanceRecord WHERE BikeID = {bike_id};"""
    query = query.format(bike_id=data['bike_id'])
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Bike removed from maintenance successfully'})


@api_view(['POST'])
@is_authenticated
def get_estimated_cost(request):
    """
    This function is used to get the estimated cost of the ride
    """
    distance = request.data.get('distance', 0)
    bike_id = request.data['bike_id']
    # hardcoded minutes required to travel distance
    # get minutes from request, if not there calculate from distance
    minutes = request.data.get('minutes', int(distance) * 2)

    cursor, conn, connection = get_cursor()
    # Call the stored procedure to calculate the rental cost
    cursor.execute("CALL CalculateRentalCostSelect(%s, %s);", [bike_id, minutes])
    result = cursor.fetchone()

    # Check if the procedure returned a result
    if result:
        bike_type, cost = result
        return Response({'cost': cost, 'bike_type': bike_type})
    else:
        return Response({'error': 'No data returned from the procedure'}, status=404)


# transaction history of the user

# api to start the ride (start station id, bike id, user id, start time, end station id)
@api_view(['POST'])
@is_authenticated
def start_ride(request):
    data = request.data
    start_station_id = data['start_station_id']
    bike_id = data['bike_id']
    user_id = request.user_id
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    end_station_id = data['end_station_id']
    end_time = None

    # insert into booking schedule
    query = """
    INSERT INTO BookingSchedule (StartDate, UserID, BikeID, StartStationID, EndStationID) VALUES ('{start_time}', {user_id}, {bike_id}, {start_station_id}, {end_station_id});"""
    query = query.format(start_time=start_time, user_id=user_id, bike_id=bike_id, start_station_id=start_station_id, end_station_id=end_station_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Ride started successfully'})


# api to end the ride (end time)
@api_view(['POST'])
@is_authenticated
def end_ride(request):
    data = request.data
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_id = request.user_id
    bike_id = data['bike_id']

    # update the booking schedule
    query = """
    UPDATE BookingSchedule SET EndDate = '{end_time}' WHERE UserID = {user_id} AND BikeID = {bike_id};"""
    query = query.format(end_time=end_time, user_id=user_id, bike_id=bike_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()

    # get schedule ScheduleID
    query = """
    SELECT ScheduleID FROM BookingSchedule WHERE UserID = {user_id} AND BikeID = {bike_id};"""
    query = query.format(user_id=user_id, bike_id=bike_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()

    return Response({'message': 'Ride ended successfully', 'ScheduleID': result[0][0]})

# make payment api
@api_view(['POST'])
@is_authenticated
def make_payment(request):
    data = request.data
    user_id = request.user_id
    schedule_id = data["ScheduleID"]
    amount = data['amount']
    #   `TransactionID` int NOT NULL,
    #   `Cost` decimal(10,2) DEFAULT NULL,
    #   `ScheduleID` int DEFAULT NULL,
    #   `UserID` int DEFAULT NULL,
    query = """
    INSERT INTO Transaction (Cost, ScheduleID, UserID) VALUES ({Cost}, {ScheduleID}, {UserID});"""
    query = query.format(Cost=amount, ScheduleID=schedule_id, UserID=user_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Payment made successfully'})

# get all payment history
@api_view(['GET'])
@is_authenticated
def get_payment_history(request):
    user_id = request.user_id
    # get the payment history
    query = """
    SELECT t.TransactionID, t.Cost, b.BikeID, t.UserID, t.ScheduleID, b.StartDate, b.EndDate , st.StationName as start_station, ed.StationName as end_station
    FROM Transaction t
    inner join BookingSchedule b on t.ScheduleID = b.ScheduleID
    inner join stations st on b.StartStationID = st.StationID
    inner join stations ed on b.EndStationID = ed.StationID
    WHERE t.UserID = {user_id}
    order by b.StartDate desc;"""
    query = query.format(user_id=user_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close_connection()

    # reformat response
    response = {}
    payments = []
    for row in result:
        payment = {
            "TransactionID": row[0],
            "Cost": row[1],
            "BikeID": row[2],
            "UserID": row[3],
            "ScheduleID": row[4],
            "start_time": row[5],
            "end_time": row[6],
            "start_station": row[7],
            "end_station": row[8]
        }
        payments.append(payment)
    return Response(payments)

@api_view(['DELETE'])
@is_authenticated
def delete_transaction(request):
    """
    This function is used to delete a user
    """
    user_id = request.user_id
    transaction_id = request.data['transaction_id']
    query = """
    DELETE FROM Transaction WHERE TransactionID = {transaction_id} AND UserID = {user_id};"""
    query = query.format(transaction_id=transaction_id, user_id=user_id)
    conn = MySQLConnector()
    connection = conn.get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    conn.close_connection()
    return Response({'message': 'Transaction deleted successfully'})




