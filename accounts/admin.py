from django.contrib import admin

from .models import Profile, Vehicle


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone_number')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'owner', 'vehicle_type', 'registered_at')
    search_fields = ('plate_number', 'owner__username')
    list_filter = ('vehicle_type',)
