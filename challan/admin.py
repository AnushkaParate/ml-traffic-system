from django.contrib import admin

from .models import Challan, Violation


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ('violation_type', 'vehicle', 'confidence_score', 'detected_at')
    list_filter = ('violation_type',)
    search_fields = ('vehicle__plate_number', 'video_source')


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ('violation', 'fine_amount', 'status', 'email_sent', 'issued_at')
    list_filter = ('status', 'email_sent')