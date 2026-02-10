from django.contrib import admin
from .models import Machine, EnergyRecord, Alert


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'workshop_area', 'rated_power_kw', 'status', 'alert_threshold_kw')
    search_fields = ('name', 'workshop_area')


@admin.register(EnergyRecord)
class EnergyRecordAdmin(admin.ModelAdmin):
    list_display = ('machine', 'power_kw', 'energy_kwh', 'timestamp')
    list_filter = ('machine',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('machine', 'alert_level', 'created_at', 'acknowledged')
    list_filter = ('alert_level', 'acknowledged')
