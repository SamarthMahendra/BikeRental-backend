# Generated by Django 5.0.3 on 2024-04-16 18:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bike',
            fields=[
                ('BikeID', models.AutoField(primary_key=True, serialize=False)),
                ('Status', models.CharField(max_length=100)),
                ('Location_lat', models.DecimalField(decimal_places=6, max_digits=10)),
                ('Location_lon', models.DecimalField(decimal_places=6, max_digits=10)),
                ('InUse', models.BooleanField()),
                ('LastMaintenanceDate', models.DateTimeField(auto_now_add=True)),
                ('RideCount', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'bike',
            },
        ),
        migrations.CreateModel(
            name='Stations',
            fields=[
                ('StationID', models.AutoField(primary_key=True, serialize=False)),
                ('Locatiion_lat', models.CharField(max_length=64)),
                ('Locatiion_lon', models.CharField(max_length=64)),
                ('Capacity', models.IntegerField()),
                ('StationName', models.CharField(max_length=255)),
                ('Address', models.TextField()),
            ],
            options={
                'db_table': 'stations',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('token', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'User',
            },
        ),
        migrations.CreateModel(
            name='MaintenanceRecord',
            fields=[
                ('RecordID', models.AutoField(primary_key=True, serialize=False)),
                ('DateOfMaintenance', models.DateField()),
                ('Details', models.CharField(max_length=255)),
                ('BikeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Rental.bike')),
            ],
            options={
                'db_table': 'maintenanceRecord',
            },
        ),
        migrations.AddField(
            model_name='bike',
            name='StationID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Rental.stations'),
        ),
    ]
