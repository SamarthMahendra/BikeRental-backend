from django.db import models

# Create your models here.

# create a model called user
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    # declare table name as User
    class Meta:
        app_label = 'Rental'
        db_table = 'User'



# create model using this schema
# -- bikerental.maintenancerecord definition
#
# CREATE TABLE `maintenancerecord` (
#   `RecordID` int NOT NULL AUTO_INCREMENT,
#   `DateOfMaintenance` date DEFAULT NULL,
#   `Details` varchar(255) DEFAULT NULL,
#   `BikeID` int DEFAULT NULL,
#   PRIMARY KEY (`RecordID`),
#   KEY `BikeID` (`BikeID`),
#   CONSTRAINT `maintenancerecord_ibfk_1` FOREIGN KEY (`BikeID`) REFERENCES `bike` (`BikeID`)
# ) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb3;

class MaintenanceRecord(models.Model):
    RecordID = models.AutoField(primary_key=True)
    DateOfMaintenance = models.DateField()
    Details = models.CharField(max_length=255)
    BikeID = models.ForeignKey('Bike', on_delete=models.CASCADE, db_column='BikeID')

    def __str__(self):
        return str(self.RecordID)

    class Meta:
        app_label = 'Rental'
        db_table = 'maintenancerecord'



# -- bikerental.stations definition
#
# CREATE TABLE `stations` (
#   `StationID` int NOT NULL,
#   `Locatiion_lat` varchar(64) DEFAULT NULL,
#   `Locatiion_lon` varchar(64) DEFAULT NULL,
#   `Capacity` int DEFAULT NULL,
#   `StationName` varchar(255) DEFAULT NULL,
#   `Address` text,
#   PRIMARY KEY (`StationID`)
# ) ENGINE=InnoDB DEFAULT

class Stations(models.Model):
    StationID = models.AutoField(primary_key=True)
    Locatiion_lat = models.CharField(max_length=64)
    Locatiion_lon = models.CharField(max_length=64)
    Capacity = models.IntegerField()
    StationName = models.CharField(max_length=255)
    Address = models.TextField()

    def __str__(self):
        return self.StationName

    class Meta:
        app_label = 'Rental'
        db_table = 'stations'

# -- bikerental.bike definition
#
# CREATE TABLE `bike` (
#   `BikeID` int NOT NULL AUTO_INCREMENT,
#   `Status` varchar(100) DEFAULT NULL,
#   `Location_lat` decimal(10,6) DEFAULT NULL,
#   `Location_lon` decimal(10,6) DEFAULT NULL,
#   `InUse` tinyint(1) DEFAULT NULL,
#   `StationID` int DEFAULT NULL,
#   `LastMaintenanceDate` datetime DEFAULT CURRENT_TIMESTAMP,
#   `RideCount` int DEFAULT '0',
#   PRIMARY KEY (`BikeID`),
#   KEY `StationID` (`StationID`),
#   CONSTRAINT `bike_ibfk_1` FOREIGN KEY (`StationID`) REFERENCES `stations` (`StationID`)
# ) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb3;

class Bike(models.Model):
    BikeID = models.AutoField(primary_key=True)
    Status = models.CharField(max_length=100)
    Location_lat = models.DecimalField(max_digits=10, decimal_places=6)
    Location_lon = models.DecimalField(max_digits=10, decimal_places=6)
    InUse = models.BooleanField()
    StationID = models.ForeignKey('Stations', on_delete=models.CASCADE, db_column='StationID')
    LastMaintenanceDate = models.DateTimeField(auto_now_add=True)
    RideCount = models.IntegerField(default=0)

    def __str__(self):
        return str(self.BikeID)

    class Meta:
        app_label = 'Rental'
        db_table = 'bike'



# -- bikerental.ebike definition
#
# CREATE TABLE `ebike` (
#   `my_row_id` bigint unsigned NOT NULL AUTO_INCREMENT /*!80023 INVISIBLE */,
#   `BikeID` int DEFAULT NULL,
#   `Bike_range` int DEFAULT NULL,
#   PRIMARY KEY (`my_row_id`),
#   UNIQUE KEY `BikeID` (`BikeID`,`Bike_range`),
#   CONSTRAINT `ebike_ibfk_1` FOREIGN KEY (`BikeID`) REFERENCES `bike` (`BikeID`)
# ) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb3;

class Ebike(models.Model):
    my_row_id = models.AutoField(primary_key=True)
    BikeID = models.ForeignKey('Bike', on_delete=models.CASCADE, db_column='BikeID')
    Bike_range = models.IntegerField()

    def __str__(self):
        return str(self.my_row_id)

    class Meta:
        app_label = 'Rental'
        db_table = 'ebike'