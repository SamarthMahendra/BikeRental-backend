from datetime import date

from django.contrib import admin

from django.contrib import admin
from .models import User, MaintenanceRecord, Stations, Bike

# Register your models here.

from django.contrib import admin

# Set the site header
admin.site.site_header = 'Blue Bikes Rental Administration'


from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import MaintenanceRecord

from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.urls import reverse
from .models import MaintenanceRecord

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('RecordID', 'DateOfMaintenance', 'Details', 'BikeID', 'mark_done_link')  # Updated to use the link method
    search_fields = ('Details',)
    list_filter = ('DateOfMaintenance',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mark-done/<int:record_id>/', self.admin_site.admin_view(self.mark_done), name='mark-done'),
        ]
        return custom_urls + urls

    def mark_done(self, request, record_id, *args, **kwargs):
        """
        The method that handles the deletion of a record.
        """
        obj = self.get_object(request, record_id)
        if obj is not None:
            obj.delete()  # Perform the deletion
            self.message_user(request, "Maintenance record marked as done and deleted.")
        # redirect to admin/Rental/bike/

        return HttpResponseRedirect("/admin/Rental/maintenancerecord/")

    def mark_done_link(self, obj):
        """
        Returns a link to the mark_done view for each record.
        """
        return format_html(
            '<a class="button" href="{}">Mark as Done</a>',
            reverse('admin:mark-done', args=[obj.pk])
        )
    mark_done_link.short_description = 'Actions'
    mark_done_link.allow_tags = True



@admin.register(Stations)
class StationsAdmin(admin.ModelAdmin):
    list_display = ('StationID', 'Locatiion_lat', 'Locatiion_lon', 'Capacity', 'StationName', 'Address')
    search_fields = ('StationName',)
    list_filter = ('Capacity',)
from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages
from .models import Bike, MaintenanceRecord
from datetime import date

@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ('BikeID', 'Status', 'Location_lat', 'Location_lon', 'InUse', 'StationID', 'maintenance_link')
    search_fields = ('Status',)
    list_filter = ('InUse', 'Status')  # Added 'Status' to filters for easier management

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:bike_id>/maintenance/',
                self.admin_site.admin_view(self.process_maintenance),
                name='bike-maintenance',
            ),
        ]
        return custom_urls + urls

    def process_maintenance(self, request, bike_id, *args, **kwargs):
        bike = self.model.objects.get(pk=bike_id)
        if bike.Status == 'Available':  # Only process if bike is available
            MaintenanceRecord.objects.create(
                BikeID=bike,
                DateOfMaintenance=date.today(),
                Details='Routine maintenance'
            )
            bike.Status = 'Maintenance'  # Update status to reflect maintenance state
            bike.save()
            messages.success(request, "Bike moved to maintenance successfully.")
        else:
            messages.error(request, "Only available bikes can be moved to maintenance.")
        return redirect('admin/Rental/bike/')

    def maintenance_link(self, obj):
        if obj.Status == 'Available':  # Display the link only if the bike is available
            return format_html(
                '<a class="button" href="{}">Move to Maintenance</a>',
                reverse('admin:bike-maintenance', args=[obj.pk])
            )
        return format_html('Unavailable for Maintenance')  # Alternative text when not available

    maintenance_link.short_description = 'Maintenance Actions'
    maintenance_link.allow_tags = True

# Ensure to update other relevant parts of your Django project as necessary.
