
# hostname=stock-bucket-indiaa.mysql.database.azure.com
# username=superuser
# password={your-password}
# ssl-mode=require


# mysql engine
import mysql.connector

# cnx = mysql.connector.connect(user="superuser", password="{your_password}", host="stock-bucket-indiaa.mysql.database.azure.com", port=3306, database="{your_database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)
class MySQLConnector:

    # sll_ca C:\Users\samar\OneDrive\Desktop\Practice projects\BikeRental\Rental\DigiCertGlobalRootCA.crt.pem
    def __init__(self):
        self.cnx = mysql.connector.connect(user="superuser", password="root@123",
                                      host="stock-bucket-indiaa.mysql.database.azure.com", port=3306,
                                      database="bikerental", ssl_ca="C:\\Users\\samar\\OneDrive\\Desktop\\Practice projects\\BikeRental\\Rental\\DigiCertGlobalRootCA.crt.pem", ssl_disabled=False)

    def get_connection(self):
        return self.cnx

    def close_connection(self):
        self.cnx.close()

    def execute_query(self, query):
        cursor = self.cnx.cursor()
        cursor.execute(query)
        return cursor.fetchall()
