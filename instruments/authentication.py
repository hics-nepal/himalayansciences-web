"""
Station API key authentication — in a standalone module to avoid DRF circular import
when referenced from REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class TokenAuthentication(BaseAuthentication):
    """Station API key authentication (SHA-256 hash comparison)."""

    def authenticate(self, request):
        key = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '').strip()
        if not key:
            return None

        station_id = (
            request.data.get('station_id')
            if hasattr(request, 'data')
            else None
        ) or request.GET.get('station')

        if not station_id:
            return None

        # Import here to avoid top-level circular imports
        from instruments.models import Station

        try:
            station = Station.objects.get(station_id=station_id)
        except Station.DoesNotExist:
            raise AuthenticationFailed('Unknown station.')

        if not station.check_api_key(key):
            raise AuthenticationFailed('Invalid API key.')

        station.last_seen = timezone.now()
        station.save(update_fields=['last_seen'])
        return (station, key)
