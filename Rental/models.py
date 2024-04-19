from django.db import models

# Create your models here.

class User(models.Model):
    UserID = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=512)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'Rental'
        db_table = 'user'



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


class Ebike(models.Model):
    my_row_id = models.AutoField(primary_key=True)
    BikeID = models.ForeignKey('Bike', on_delete=models.CASCADE, db_column='BikeID')
    Bike_range = models.IntegerField()

    def __str__(self):
        return str(self.my_row_id)

    class Meta:
        app_label = 'Rental'
        db_table = 'ebike'


class BookingSchedule(models.Model):
    ScheduleID = models.AutoField(primary_key=True)
    StartDate = models.DateTimeField()
    EndDate = models.DateTimeField()
    UserID = models.ForeignKey('User', on_delete=models.CASCADE, db_column='UserID')
    BikeID = models.ForeignKey('Bike', on_delete=models.CASCADE, db_column='BikeID')
    StartStationID = models.ForeignKey('Stations', on_delete=models.CASCADE, db_column='StartStationID', related_name='start_station')
    EndStationID = models.ForeignKey('Stations', on_delete=models.CASCADE, db_column='EndStationID', related_name='end_station')

    def __str__(self):
         return str( "UserID: " + str(self.UserID) + " BikeID: " + str(self.BikeID) + " StartStationID: " + str(self.StartStationID) + " EndStationID: " + str(self.EndStationID))

    class Meta:
        app_label = 'Rental'
        db_table = 'bookingschedule'


class Feedback(models.Model):
    FeedbackID = models.AutoField(primary_key=True)
    Rating = models.IntegerField()
    Comments = models.CharField(max_length=1024)
    ScheduleID = models.ForeignKey('BookingSchedule', on_delete=models.CASCADE, db_column='ScheduleID', related_name='ride')
    Timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.FeedbackID)

    class Meta:
        app_label = 'Rental'
        db_table = 'feedback'

class StationRevenueSummary(models.Model):
    StationID = models.ForeignKey('Stations', on_delete=models.CASCADE, db_column='StationID', primary_key=True)
    StationName = models.CharField(max_length=255)
    TotalRides = models.IntegerField(default=0)
    TotalEBikeRides = models.IntegerField(default=0)
    TotalClassicBikeRides = models.IntegerField(default=0)
    TotalRevenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.StationID)

    class Meta:
        app_label = 'Rental'
        db_table = 'station_revenue_summary'
