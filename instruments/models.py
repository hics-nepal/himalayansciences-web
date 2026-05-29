from django.db import models
import hashlib
import secrets


class Station(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
        ('planned', 'Planned'),
    ]
    station_id = models.CharField(max_length=20, unique=True)  # KTM-001
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude_m = models.FloatField()
    location_name = models.CharField(max_length=100)           # "Kathmandu"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    api_key_hash = models.CharField(max_length=64)             # SHA-256 of key
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def set_api_key(self, key):
        self.api_key_hash = hashlib.sha256(key.encode()).hexdigest()

    def check_api_key(self, key):
        return self.api_key_hash == hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def generate_api_key(cls):
        return secrets.token_urlsafe(32)

    def __str__(self):
        return f"{self.station_id} — {self.name}"

    class Meta:
        ordering = ['station_id']


class EnvironmentalReading(models.Model):
    station = models.ForeignKey(Station, on_delete=models.PROTECT,
                                related_name='readings')
    timestamp = models.DateTimeField(db_index=True)
    temperature_c = models.FloatField(null=True, blank=True)
    humidity_rh = models.FloatField(null=True, blank=True)
    pressure_hpa = models.FloatField(null=True, blank=True)
    altitude_m = models.FloatField(null=True, blank=True)
    pm1_0 = models.FloatField(null=True, blank=True)
    pm2_5 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    co2_ppm = models.FloatField(null=True, blank=True)
    co_ppm = models.FloatField(null=True, blank=True)
    uv_index = models.FloatField(null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['station', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.station.station_id} @ {self.timestamp}"


class MeteorDetection(models.Model):
    station = models.ForeignKey(Station, on_delete=models.PROTECT,
                                related_name='meteor_detections')
    timestamp = models.DateTimeField(db_index=True)
    image = models.ImageField(upload_to='meteors/%Y/%m/')
    thumbnail = models.ImageField(upload_to='meteors/thumbs/%Y/%m/',
                                  null=True, blank=True)
    magnitude = models.FloatField(null=True, blank=True)
    duration_s = models.FloatField(null=True, blank=True)
    shower_association = models.CharField(max_length=50, blank=True)
    confirmed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
