from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.http import StreamingHttpResponse
import csv
import io

from .models import Station, EnvironmentalReading
from .authentication import TokenAuthentication  # noqa: F401 — re-exported for convenience


class IngestEnvironmentalView(APIView):
    """Receive batch readings from an IESH station."""

    def post(self, request):
        station = request.user  # set by TokenAuthentication
        readings_data = request.data.get('readings', [])
        if not readings_data:
            return Response({'error': 'No readings provided.'}, status=400)

        created = 0
        for r in readings_data:
            try:
                EnvironmentalReading.objects.get_or_create(
                    station=station,
                    timestamp=r['timestamp'],
                    defaults={
                        'temperature_c': r.get('temperature_c'),
                        'humidity_rh': r.get('humidity_rh'),
                        'pressure_hpa': r.get('pressure_hpa'),
                        'altitude_m': r.get('altitude_m'),
                        'pm2_5': r.get('pm2_5'),
                        'pm10': r.get('pm10'),
                        'co2_ppm': r.get('co2_ppm'),
                    }
                )
                created += 1
            except Exception:
                continue

        return Response({'accepted': created}, status=201)


class LatestReadingView(APIView):
    """Public: latest reading for a station."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        station_id = request.GET.get('station', 'KTM-001')
        try:
            reading = EnvironmentalReading.objects.filter(
                station__station_id=station_id
            ).latest('timestamp')
            station = reading.station
            return Response({
                'station_id': station.station_id,
                'station_name': station.name,
                'location': station.location_name,
                'altitude_m': station.altitude_m,
                'latitude': station.latitude,
                'longitude': station.longitude,
                'timestamp': reading.timestamp,
                'temperature_c': reading.temperature_c,
                'humidity_rh': reading.humidity_rh,
                'pressure_hpa': reading.pressure_hpa,
                'pm2_5': reading.pm2_5,
                'pm10': reading.pm10,
                'co2_ppm': reading.co2_ppm,
            })
        except EnvironmentalReading.DoesNotExist:
            return Response({'error': 'No data yet.'}, status=404)


class HistoricalDataView(APIView):
    """Public: time series for a station + sensor."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        station_id = request.GET.get('station', 'KTM-001')
        hours = int(request.GET.get('hours', 24))
        since = timezone.now() - timezone.timedelta(hours=hours)

        readings = EnvironmentalReading.objects.filter(
            station__station_id=station_id,
            timestamp__gte=since
        ).order_by('timestamp').values(
            'timestamp', 'temperature_c', 'humidity_rh',
            'pressure_hpa', 'pm2_5', 'pm10', 'co2_ppm'
        )
        return Response(list(readings))


class DownloadCSVView(APIView):
    """Public: download full dataset as CSV."""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        station_id = request.GET.get('station', 'KTM-001')
        readings = EnvironmentalReading.objects.filter(
            station__station_id=station_id
        ).order_by('timestamp').values_list(
            'timestamp', 'temperature_c', 'humidity_rh',
            'pressure_hpa', 'pm2_5', 'pm10', 'co2_ppm'
        )

        def stream():
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow([
                'timestamp_utc', 'temperature_c', 'humidity_rh',
                'pressure_hpa', 'pm2_5_ugm3', 'pm10_ugm3', 'co2_ppm'
            ])
            yield buf.getvalue()
            for row in readings.iterator(chunk_size=500):
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(row)
                yield buf.getvalue()

        response = StreamingHttpResponse(stream(), content_type='text/csv')
        response['Content-Disposition'] = \
            f'attachment; filename="HICS_{station_id}_environmental.csv"'
        return response
