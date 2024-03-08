
# hostname=stock-bucket-indiaa.mysql.database.azure.com
# username=superuser
# password={your-password}
# ssl-mode=require


# mysql engine
import mysql.connector

# cnx = mysql.connector.connect(user="superuser", password="{your_password}", host="stock-bucket-indiaa.mysql.database.azure.com", port=3306, database="{your_database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)
class MySQLConnector:

    def __init__(self):
        self.cnx = mysql.connector.connect(
            user="superuser",
            password="root@123",
            host="stock-bucket-indiaa.mysql.database.azure.com",
            port=3306,
            database="bikerental"
        )

    def get_connection(self):
        return self.cnx

    def close_connection(self):
        self.cnx.close()

    def execute_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        return cursor.fetchall()
