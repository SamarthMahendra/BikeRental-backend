import mysql.connector

class MySQLConnector:
    _instances = {}
    _instance_count = 0
    _max_instances = 100

    def __new__(cls):
        if cls._instance_count < cls._max_instances:
            instance = super().__new__(cls)
            cls._instances[cls._instance_count] = instance
            cls._instance_count += 1
            return instance
        else:
            raise Exception("Maximum instance limit reached")

    def __init__(self):
        # We initialize only if not already initialized
        if not hasattr(self, 'initialized'):
            self.cnx = mysql.connector.connect(
                user="superuser", password="root@123",
                host="stock-bucket-indiaa.mysql.database.azure.com", port=3306,
                database="bikerental",
                ssl_ca="C:\\Users\\samar\\OneDrive\\Desktop\\Practice projects\\BikeRental\\Rental\\DigiCertGlobalRootCA.crt.pem",
                ssl_disabled=False
            )
            self.initialized = True

    def get_connection(self):
        return self.cnx

    def close_connection(self):
        self.cnx.close()

    def execute_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        return cursor.fetchall()


def get_cursor():
    conn = MySQLConnector()
    connection = conn.get_connection()
    return connection.cursor(), conn
