from django.contrib import admin
from .models import Station, EnvironmentalReading, MeteorDetection


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('station_id', 'name', 'location_name', 'altitude_m', 'status', 'last_seen')
    list_filter = ('status',)
    search_fields = ('station_id', 'name', 'location_name')
    readonly_fields = ('created_at', 'last_seen')


@admin.register(EnvironmentalReading)
class EnvironmentalReadingAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'temperature_c', 'humidity_rh', 'pressure_hpa', 'pm2_5')
    list_filter = ('station',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('received_at',)


@admin.register(MeteorDetection)
class MeteorDetectionAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'magnitude', 'shower_association', 'confirmed')
    list_filter = ('station', 'confirmed', 'shower_association')
    date_hierarchy = 'timestamp'
    readonly_fields = ('received_at',)
