import mysql.connector


class MySQLConnector:
    def __init__(self):
        # Initialize a new connection whenever a new instance is created
        self.cnx = mysql.connector.connect(
            user="superuser", password="root@123",
            host="stock-bucket-indiaa.mysql.database.azure.com", port=3306,
            database="bikerental",
            ssl_ca="Rental/DigiCertGlobalRootCA.crt.pem",
            ssl_disabled=False
        )

    def get_connection(self):
        return self.cnx

    def close_connection(self):
        self.cnx.close()

    def execute_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        return cursor.fetchall()

# Usage


def get_cursor():
    conn = MySQLConnector()  # Creates a new instance and hence a new connection each time
    connection = conn.get_connection()
    return connection.cursor(), conn, connection
