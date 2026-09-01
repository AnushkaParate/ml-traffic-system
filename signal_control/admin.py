from django.contrib import admin

from .models import SignalLog


@admin.register(SignalLog)
class SignalLogAdmin(admin.ModelAdmin):
    list_display = ('intersection_id', 'lane', 'vehicle_count', 'ambulance_detected', 'signal_state', 'timestamp')
    list_filter = ('signal_state', 'ambulance_detected')