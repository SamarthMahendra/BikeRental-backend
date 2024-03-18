from django.core.management.base import BaseCommand
from Rental.sqlconnector import MySQLConnector


# write management to run the script
class Command(BaseCommand):
    help = 'initialize the database'

    # python manage.py initialize_db

    def handle(self, *args, **kwargs):
        from .queries import create_table_commands
        mapping = {
            # 'Stations': create_table_commands.stations_create_sql,
            'User': create_table_commands.user_create_sql,
            'Bike': create_table_commands.bike_create_sql,
            'BikeCard': create_table_commands.bike_card_create_sql,
            'Rate': create_table_commands.rate_create_sql,
            'Transaction': create_table_commands.transaction_create_sql,
            'MaintenanceRecord': create_table_commands.maintenance_record_create_sql,
            'BookingSchedule': create_table_commands.booking_schedule_create_sql,
            'Feedback': create_table_commands.feedback_create_sql,
            'PaymentHistory': create_table_commands.payment_history_create_sql,
            'LocationHistory': create_table_commands.location_history_create_sql,
            'Classic': create_table_commands.classic_create_sql,
            'Ebike': create_table_commands.ebike_create_sql
        }

        # create the tables
        # pre_run = " drop table User if exists;"
        conn = MySQLConnector()
        connection = conn.get_connection()
        cursor = connection.cursor()
        # cursor.execute(pre_run)
        for key, value in mapping.items():
            cursor.execute(value)
        connection.commit()
        conn.close_connection()
        print("Tables created successfully");