

from django.core.management.base import BaseCommand
from Rental.sqlconnector import MySQLConnector
import requests
import json
from datetime import datetime
from Rental.models import Stations

class Command(BaseCommand):
    help = 'Harvest the stations from BlueBikes API'

    def handle(self, *args, **kwargs):
        # api endpoint
        url = 'https://account.bluebikes.com/bikesharefe-gql'
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'sessId=2862fa3f-7941-48d2-b6e0-89aac5865a62L1713394921'
        }
        payload = {
            "operationName": "GetSystemSupply",
            "variables": {
                "input": {
                    "regionCode": "BOS",
                    "rideablePageLimit": 1000
                }
            },
            "query": """query GetSystemSupply($input: SupplyInput) {\n  supply(input: $input) {\n    stations {\n      stationId\n      stationName\n      location {\n        lat\n        lng\n        __typename\n      }\n      bikesAvailable\n      bikeDocksAvailable\n      ebikesAvailable\n      scootersAvailable\n      totalBikesAvailable\n      totalRideablesAvailable\n      isValet\n      isOffline\n      isLightweight\n      notices {\n        ...NoticeFields\n        __typename\n      }\n      siteId\n      ebikes {\n        batteryStatus {\n          distanceRemaining {\n            value\n            unit\n            __typename\n          }\n          percent\n          __typename\n        }\n        __typename\n      }\n      scooters {\n        batteryStatus {\n          distanceRemaining {\n            value\n            unit\n            __typename\n          }\n          percent\n          __typename\n        }\n        __typename\n      }\n      lastUpdatedMs\n      __typename\n    }\n    rideables {\n      rideableId\n      location {\n        lat\n        lng\n        __typename\n      }\n      rideableType\n      batteryStatus {\n        distanceRemaining {\n          value\n          unit\n          __typename\n        }\n        percent\n        __typename\n      }\n      __typename\n    }\n    notices {\n      ...NoticeFields\n      __typename\n    }\n    requestErrors {\n      ...NoticeFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment NoticeFields on Notice {\n  localizedTitle\n
    localizedDescription\n  url\n  __typename\n}"""
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        stations = data['data']['supply']['stations']
        i = 1000
        for station in stations:
            print(str(i) + " : " + str(station['stationName']))
            i += 1
            station_id = i
            station_name = station['stationName']
            location_lat = station['location']['lat']
            location_lon = station['location']['lng']
            capacity = station['bikeDocksAvailable']
            address = station['stationName']
            query ="""
            INSERT INTO Stations (StationID, Locatiion_lat, Locatiion_lon, Capacity, StationName, Address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            conn = MySQLConnector()
            connection = conn.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, (station_id, location_lat, location_lon, capacity, station_name, address))
            connection.commit()
            conn.close_connection()
        print("Stations harvested successfully.")


