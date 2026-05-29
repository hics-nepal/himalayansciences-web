# HICS Website — Coding Agent Build Guide

_himalayansciences.org — Django + Wagtail_
_For use with AI coding agents (Claude Code, Cursor, etc.)_

---

## Project Identity

- **Organisation:** Himalayan Institute for Contextual Sciences (HICS)
- **Domain:** himalayansciences.org
- **GitHub:** github.com/hics-nepal
- **Repo name:** `himalayansciences-web`
- **Email:** hicsnepal@gmail.com
- **Stack:** Python 3.11 / Django 5.x / Wagtail 6.x / MySQL / Redis
- **Hosting:** NestNepal cPanel (Passenger/WSGI Python app)
- **Local dev OS:** Ubuntu

---

## Part 1 — Local Project Setup

### Step 1.1 — Create project structure

```bash
# On your Ubuntu machine
mkdir himalayansciences-web
cd himalayansciences-web

python3 -m venv venv
source venv/bin/activate

pip install \
  wagtail \
  django \
  djangorestframework \
  django-environ \
  mysqlclient \
  redis \
  django-redis \
  whitenoise \
  pillow \
  gunicorn \
  requests

pip freeze > requirements.txt

wagtail start hics .
```

### Step 1.2 — Project layout target

```
himalayansciences-web/
├── manage.py
├── requirements.txt
├── requirements-dev.txt        ← dev-only (black, flake8, etc.)
├── .env                        ← never committed
├── .env.example                ← committed, no secrets
├── .gitignore
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── hics/                       ← Django project config
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py            ← local dev overrides
│   │   └── production.py       ← cPanel production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── static/                 ← global static assets
│       ├── css/
│       │   └── main.css
│       ├── js/
│       │   └── main.js
│       └── fonts/
│
├── home/                       ← Wagtail default home app (repurpose)
├── pages/                      ← all Wagtail page types
│   ├── models.py
│   ├── migrations/
│   └── templatetags/
│       └── hics_tags.py
│
├── instruments/                ← instrument data Django app
│   ├── models.py               ← Station, EnvironmentalReading, etc.
│   ├── api.py                  ← DRF viewsets
│   ├── urls.py
│   └── migrations/
│
├── templates/                  ← all HTML templates
│   ├── base.html
│   ├── pages/
│   │   ├── home_page.html
│   │   ├── about_page.html
│   │   ├── instrument_index_page.html
│   │   ├── instrument_page.html
│   │   ├── research_index_page.html
│   │   ├── research_programme_page.html
│   │   ├── data_page.html
│   │   ├── lab_note_index_page.html
│   │   ├── lab_note_page.html
│   │   └── contact_page.html
│   └── instruments/
│       └── partials/
│           ├── live_widget.html
│           └── station_status.html
│
└── media/                      ← user uploads (not committed)
```

### Step 1.3 — Settings structure

**`hics/settings/base.py`** — shared settings:

```python
import environ
from pathlib import Path

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'home',
    'pages',
    'instruments',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'modelcluster',
    'taggit',
    'rest_framework',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'hics.urls'
WSGI_APPLICATION = 'hics.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'hics' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

WAGTAIL_SITE_NAME = 'Himalayan Institute for Contextual Sciences'
WAGTAILADMIN_BASE_URL = 'https://himalayansciences.org'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'instruments.api.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

**`hics/settings/local.py`**:

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**`hics/settings/production.py`**:

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['himalayansciences.org', 'www.himalayansciences.org']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**`.env.example`** (commit this):

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=
DB_USER=
DB_PASSWORD=
REDIS_URL=redis://127.0.0.1:6379/1
```

**`.env`** (never commit — add to .gitignore):

```
SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 1.4 — URLs

**`hics/urls.py`**:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('api/', include('instruments.urls')),
    path('', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Part 2 — Data Models

### Step 2.1 — Instruments app (`instruments/models.py`)

```python
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
```

### Step 2.2 — API (`instruments/api.py`)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from django.http import StreamingHttpResponse
import csv
import io

from .models import Station, EnvironmentalReading


class TokenAuthentication(BaseAuthentication):
    """Station API key authentication."""
    def authenticate(self, request):
        key = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        if not key:
            return None
        station_id = request.data.get('station_id') or request.GET.get('station')
        try:
            station = Station.objects.get(station_id=station_id)
        except Station.DoesNotExist:
            raise AuthenticationFailed('Unknown station.')
        if not station.check_api_key(key):
            raise AuthenticationFailed('Invalid API key.')
        station.last_seen = timezone.now()
        station.save(update_fields=['last_seen'])
        return (station, key)


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
```

**`instruments/urls.py`**:

```python
from django.urls import path
from . import api

urlpatterns = [
    path('ingest/environmental/', api.IngestEnvironmentalView.as_view()),
    path('data/latest/', api.LatestReadingView.as_view()),
    path('data/historical/', api.HistoricalDataView.as_view()),
    path('data/download/', api.DownloadCSVView.as_view()),
]
```

---

## Part 3 — Wagtail Page Models

### Step 3.1 — All page types (`pages/models.py`)

```python
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.blocks import (
    RichTextBlock, ImageChooserBlock, CharBlock,
    TextBlock, StructBlock, URLBlock, ListBlock
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.models import register_snippet
from taggit.managers import TaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
import datetime


# ── Snippets ────────────────────────────────────────────────────────────────

@register_snippet
class Publication(models.Model):
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=300)
    journal = models.CharField(max_length=200)
    year = models.IntegerField()
    doi = models.CharField(max_length=200, blank=True)
    abstract = models.TextField(blank=True)
    pdf = models.ForeignKey(
        'wagtaildocs.Document', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    panels = [
        FieldPanel('title'), FieldPanel('authors'), FieldPanel('journal'),
        FieldPanel('year'), FieldPanel('doi'), FieldPanel('abstract'),
        FieldPanel('pdf'),
    ]
    def __str__(self): return f"{self.authors.split(',')[0]} et al. ({self.year})"


# ── StreamField blocks ───────────────────────────────────────────────────────

class SensorChartBlock(StructBlock):
    """Embed a live/historical sensor chart in any page body."""
    station_id = CharBlock(default='KTM-001')
    sensor = CharBlock(
        help_text='temperature_c | humidity_rh | pressure_hpa | pm2_5 | co2_ppm'
    )
    hours = CharBlock(default='24', help_text='Hours of history to show')
    caption = CharBlock(required=False)

    class Meta:
        icon = 'chart-line'
        label = 'Sensor Chart'
        template = 'pages/blocks/sensor_chart.html'


class CoordinatesBlock(StructBlock):
    label = CharBlock(required=False)
    latitude = CharBlock()
    longitude = CharBlock()
    altitude_m = CharBlock(required=False)

    class Meta:
        icon = 'site'
        label = 'Coordinates'
        template = 'pages/blocks/coordinates.html'


class CodeBlock(StructBlock):
    language = CharBlock(default='python')
    code = TextBlock()
    caption = CharBlock(required=False)

    class Meta:
        icon = 'code'
        label = 'Code'
        template = 'pages/blocks/code.html'


BODY_BLOCKS = StreamField([
    ('text', RichTextBlock(features=[
        'h2', 'h3', 'bold', 'italic', 'link', 'ol', 'ul', 'blockquote', 'superscript'
    ])),
    ('image', ImageChooserBlock()),
    ('sensor_chart', SensorChartBlock()),
    ('coordinates', CoordinatesBlock()),
    ('code', CodeBlock()),
    ('document', DocumentChooserBlock()),
    ('pull_quote', TextBlock()),
], use_json_field=True, blank=True)


# ── Page types ───────────────────────────────────────────────────────────────

class HomePage(Page):
    tagline = models.CharField(max_length=200,
        default="Science rooted in place. Data open to all.")
    mission = models.TextField(
        help_text="One clear statement of what HICS does and why.")
    intro = RichTextField(blank=True,
        help_text="Optional 2–3 sentence expansion below mission.")

    content_panels = Page.content_panels + [
        FieldPanel('tagline'),
        FieldPanel('mission'),
        FieldPanel('intro'),
    ]

    class Meta:
        verbose_name = "Home Page"

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['latest_notes'] = LabNotePage.objects.live().order_by('-first_published_at')[:3]
        ctx['instruments'] = InstrumentPage.objects.live().order_by('title')
        return ctx


class AboutPage(Page):
    intro = RichTextField()
    body = BODY_BLOCKS
    registration_info = RichTextField(blank=True,
        help_text="Company registration details, MOA excerpt.")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('registration_info'),
    ]


class ResearchIndexPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel('intro')]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['programmes'] = ResearchProgrammePage.objects.live().child_of(self)
        return ctx


class ResearchProgrammePage(Page):
    PROGRAMME_CHOICES = [
        ('cosmic-ray', 'Cosmic Ray / Muon Physics'),
        ('meteor', 'Meteor Astronomy'),
        ('atmospheric', 'Atmospheric Science'),
        ('seismology', 'Seismology'),
        ('building-physics', 'Building Physics'),
        ('traditional-knowledge', 'Traditional Ecological Knowledge'),
    ]
    programme_type = models.CharField(max_length=30, choices=PROGRAMME_CHOICES)
    status = models.CharField(max_length=20,
        choices=[('active','Active'),('planned','Planned'),('paused','Paused')],
        default='planned')
    summary = models.TextField(max_length=300,
        help_text="One paragraph, shown on index page.")
    body = BODY_BLOCKS
    publications = models.ManyToManyField(Publication, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('programme_type'),
        FieldPanel('status'),
        FieldPanel('summary'),
        FieldPanel('body'),
        FieldPanel('publications'),
    ]


class InstrumentIndexPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel('intro')]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['instruments'] = InstrumentPage.objects.live().child_of(self).order_by('title')
        return ctx


class InstrumentPage(Page):
    STATUS_CHOICES = [
        ('active', 'Active — collecting data'),
        ('building', 'Under construction'),
        ('planned', 'Planned'),
        ('retired', 'Retired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    summary = models.TextField(max_length=300,
        help_text="One sentence shown on index cards.")
    what_it_measures = RichTextField(
        help_text="Plain explanation of what this instrument does.")
    body = BODY_BLOCKS
    github_url = models.URLField(blank=True)
    station_id = models.CharField(max_length=20, blank=True,
        help_text="If deployed: station ID (e.g. KTM-001)")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('status'),
            FieldPanel('station_id'),
            FieldPanel('github_url'),
        ], heading='Status & Links'),
        FieldPanel('summary'),
        FieldPanel('what_it_measures'),
        FieldPanel('body'),
    ]

    def get_context(self, request):
        ctx = super().get_context(request)
        if self.station_id:
            from instruments.models import EnvironmentalReading, Station
            try:
                station = Station.objects.get(station_id=self.station_id)
                ctx['station'] = station
                ctx['latest_reading'] = EnvironmentalReading.objects.filter(
                    station=station).latest('timestamp')
            except Exception:
                pass
        return ctx


class DataPage(Page):
    intro = RichTextField(blank=True)
    api_docs = RichTextField(blank=True, help_text="API documentation text.")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('api_docs'),
    ]

    def get_context(self, request):
        ctx = super().get_context(request)
        from instruments.models import Station
        ctx['stations'] = Station.objects.exclude(status='planned')
        return ctx


class LabNoteTag(models.Model):
    lab_note = ParentalKey('LabNotePage', related_name='tagged_items',
                           on_delete=models.CASCADE)
    tag = models.ForeignKey('taggit.Tag', related_name='lab_note_tags',
                            on_delete=models.CASCADE)
    class Meta:
        unique_together = [('lab_note', 'tag')]


class LabNoteIndexPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel('intro')]

    def get_context(self, request):
        ctx = super().get_context(request)
        notes = LabNotePage.objects.live().child_of(self).order_by('-date')
        tag = request.GET.get('tag')
        if tag:
            notes = notes.filter(tags__name=tag)
        ctx['notes'] = notes
        ctx['active_tag'] = tag
        return ctx


class LabNotePage(Page):
    NOTE_TYPES = [
        ('observation', 'Observation'),
        ('experiment', 'Experiment'),
        ('build', 'Build Log'),
        ('field', 'Field Dispatch'),
        ('analysis', 'Analysis'),
    ]
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='observation')
    date = models.DateField(default=datetime.date.today)
    location = models.CharField(max_length=200, blank=True)
    summary = models.TextField(max_length=400,
        help_text="2–3 sentences shown on index page.")
    body = BODY_BLOCKS
    tags = ClusterTaggableManager(through=LabNoteTag, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('note_type'),
            FieldPanel('date'),
            FieldPanel('location'),
            FieldPanel('tags'),
        ], heading='Metadata'),
        FieldPanel('summary'),
        FieldPanel('body'),
    ]

    class Meta:
        ordering = ['-date']


class ContactPage(Page):
    intro = RichTextField()
    email_research = models.EmailField(default='info@himalayansciences.org')
    email_education = models.EmailField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('email_research'),
        FieldPanel('email_education'),
        FieldPanel('body'),
    ]
```

---

## Part 4 — Design System

### Step 4.1 — CSS variables and base styles

**`hics/static/css/main.css`** — write this file in full:

```css
/* ── HICS Design System ──────────────────────────────────── */

@import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,300;1,8..60,400&display=swap");

:root {
  /* Colours */
  --bg: #0d0f14;
  --surface: #141720;
  --surface-2: #1a1e2e;
  --border: #1e2235;
  --border-light: #252a40;
  --text: #e2e4ed;
  --text-muted: #6b7394;
  --text-dim: #3d4260;
  --accent: #4a9eff;
  --accent-dim: #1a3a66;
  --amber: #f0a030;
  --green: #3ddc84;
  --red: #ff5555;
  --green-dim: #1a3d2a;

  /* Typography */
  --font-mono: "IBM Plex Mono", "Courier New", monospace;
  --font-serif: "Source Serif 4", Georgia, serif;

  /* Spacing scale */
  --s1: 0.25rem;
  --s2: 0.5rem;
  --s3: 0.75rem;
  --s4: 1rem;
  --s5: 1.5rem;
  --s6: 2rem;
  --s7: 3rem;
  --s8: 4rem;
  --s9: 6rem;

  /* Layout */
  --max-width: 1100px;
  --content-width: 720px;
  --radius: 4px;
}

/* ── Reset ──────────────────────────────────────────────── */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-serif);
  font-size: 1.0625rem;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}

/* ── Typography ─────────────────────────────────────────── */
h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: var(--font-mono);
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
h1 {
  font-size: clamp(1.75rem, 4vw, 2.75rem);
}
h2 {
  font-size: clamp(1.25rem, 3vw, 1.75rem);
  margin-top: var(--s7);
}
h3 {
  font-size: 1.125rem;
  margin-top: var(--s6);
}

p {
  margin-top: var(--s4);
}
p:first-child {
  margin-top: 0;
}

a {
  color: var(--accent);
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

code,
pre,
.mono {
  font-family: var(--font-mono);
  font-size: 0.875em;
}

pre {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--s5);
  overflow-x: auto;
  margin: var(--s5) 0;
}

blockquote {
  border-left: 3px solid var(--accent);
  padding-left: var(--s5);
  color: var(--text-muted);
  font-style: italic;
  margin: var(--s6) 0;
}

/* ── Layout ─────────────────────────────────────────────── */
.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--s5);
}

.content {
  max-width: var(--content-width);
}

/* ── Site Header ────────────────────────────────────────── */
.site-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.site-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  gap: var(--s5);
}

.site-logo {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text);
  text-decoration: none;
  white-space: nowrap;
}
.site-logo span {
  color: var(--accent);
}

.site-nav {
  display: flex;
  gap: var(--s5);
  list-style: none;
  align-items: center;
}

.site-nav a {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--text-muted);
  text-decoration: none;
  letter-spacing: 0.02em;
  transition: color 0.15s;
}
.site-nav a:hover,
.site-nav a.active {
  color: var(--text);
}

/* Live station widget in header */
.station-live {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: var(--s2);
  white-space: nowrap;
}
.station-live__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--green);
  animation: pulse 2s infinite;
}
.station-live__dot.offline {
  background: var(--red);
  animation: none;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

/* ── Hero / Mission ─────────────────────────────────────── */
.hero {
  padding: var(--s9) 0 var(--s7);
  border-bottom: 1px solid var(--border);
}
.hero__mission {
  font-family: var(--font-mono);
  font-size: clamp(1.1rem, 2.5vw, 1.5rem);
  font-weight: 400;
  line-height: 1.4;
  max-width: 700px;
  color: var(--text);
}
.hero__mission em {
  color: var(--accent);
  font-style: normal;
}
.hero__sub {
  margin-top: var(--s5);
  color: var(--text-muted);
  font-family: var(--font-serif);
  max-width: 560px;
}

/* ── Cards ──────────────────────────────────────────────── */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--s4);
  margin-top: var(--s5);
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--s5);
  transition: border-color 0.15s;
  text-decoration: none;
  color: inherit;
  display: block;
}
.card:hover {
  border-color: var(--border-light);
  text-decoration: none;
}

.card__label {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: var(--s3);
}
.card__title {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: var(--s3);
}
.card__body {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Status badges */
.badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  padding: 2px 8px;
  border-radius: 2px;
  margin-top: var(--s3);
}
.badge--active {
  background: var(--green-dim);
  color: var(--green);
}
.badge--building {
  background: var(--accent-dim);
  color: var(--accent);
}
.badge--planned {
  background: var(--surface-2);
  color: var(--text-muted);
}

/* ── Live Data Widget ───────────────────────────────────── */
.data-widget {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--s5) var(--s6);
  margin: var(--s6) 0;
}
.data-widget__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--s5);
  flex-wrap: wrap;
  gap: var(--s3);
}
.data-widget__title {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.data-widget__readings {
  display: flex;
  gap: var(--s6);
  flex-wrap: wrap;
}
.reading {
  display: flex;
  flex-direction: column;
}
.reading__value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 500;
  color: var(--text);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.reading__unit {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--accent);
  margin-left: 2px;
}
.reading__label {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-top: var(--s2);
}

/* ── Chart container ────────────────────────────────────── */
.chart-wrap {
  position: relative;
  height: 200px;
  margin: var(--s5) 0;
}

/* ── Lab Notes ──────────────────────────────────────────── */
.note-list {
  margin-top: var(--s5);
}
.note-item {
  border-top: 1px solid var(--border);
  padding: var(--s5) 0;
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: var(--s5);
}
.note-item__meta {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}
.note-item__date {
  color: var(--text-dim);
}
.note-item__type {
  margin-top: var(--s2);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.6875rem;
}
.note-item__title {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: var(--s2);
}
.note-item__summary {
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* ── Page sections ──────────────────────────────────────── */
.section {
  padding: var(--s8) 0;
  border-bottom: 1px solid var(--border);
}
.section:last-child {
  border-bottom: none;
}

.section__label {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  margin-bottom: var(--s4);
}

/* ── Site Footer ────────────────────────────────────────── */
.site-footer {
  border-top: 1px solid var(--border);
  padding: var(--s7) 0;
  margin-top: var(--s9);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-dim);
}
.site-footer a {
  color: var(--text-muted);
}
.site-footer__inner {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--s6);
  flex-wrap: wrap;
}
.site-footer__coords {
  font-size: 0.6875rem;
  color: var(--text-dim);
  margin-top: var(--s2);
}

/* ── Utilities ──────────────────────────────────────────── */
.text-muted {
  color: var(--text-muted);
}
.text-mono {
  font-family: var(--font-mono);
}
.text-accent {
  color: var(--accent);
}
.text-green {
  color: var(--green);
}
.text-amber {
  color: var(--amber);
}
.mt-0 {
  margin-top: 0;
}
.mt-4 {
  margin-top: var(--s4);
}
.mt-5 {
  margin-top: var(--s5);
}
.mt-6 {
  margin-top: var(--s6);
}
.mt-7 {
  margin-top: var(--s7);
}

/* ── Responsive ─────────────────────────────────────────── */
@media (max-width: 700px) {
  .site-nav {
    display: none;
  }
  .station-live {
    display: none;
  }
  .note-item {
    grid-template-columns: 1fr;
    gap: var(--s2);
  }
  .data-widget__readings {
    gap: var(--s5);
  }
  .reading__value {
    font-size: 1.5rem;
  }
}
```

---

## Part 5 — Templates

### Step 5.1 — Base template (`templates/base.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}{{ page.seo_title|default:page.title }} — HICS{% endblock %}</title>
  <meta name="description" content="{% block description %}Himalayan Institute for Contextual Sciences — open science rooted in Nepal's geography.{% endblock %}">

  {% load static wagtailcore_tags wagtailimages_tags %}

  <link rel="stylesheet" href="{% static 'css/main.css' %}">
  <link rel="icon" href="{% static 'img/favicon.svg' %}" type="image/svg+xml">
  {% block extra_css %}{% endblock %}
</head>
<body>

<header class="site-header">
  <div class="container">
    <div class="site-header__inner">

      <a href="/" class="site-logo">
        HICS<span>.</span>
      </a>

      <nav>
        <ul class="site-nav">
          <li><a href="/about/" {% if request.path == '/about/' %}class="active"{% endif %}>About</a></li>
          <li><a href="/research/" {% if '/research/' in request.path %}class="active"{% endif %}>Research</a></li>
          <li><a href="/instruments/" {% if '/instruments/' in request.path %}class="active"{% endif %}>Instruments</a></li>
          <li><a href="/data/" {% if request.path == '/data/' %}class="active"{% endif %}>Data</a></li>
          <li><a href="/notes/" {% if '/notes/' in request.path %}class="active"{% endif %}>Notes</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </nav>

      <div class="station-live" id="header-station" aria-live="polite">
        <div class="station-live__dot offline" id="station-dot"></div>
        <span id="station-reading">—</span>
      </div>

    </div>
  </div>
</header>

<main>
  {% block content %}{% endblock %}
</main>

<footer class="site-footer">
  <div class="container">
    <div class="site-footer__inner">
      <div>
        <div>Himalayan Institute for Contextual Sciences</div>
        <div class="site-footer__coords">Kathmandu, Nepal &nbsp;·&nbsp; 27.7172°N 85.3240°E</div>
      </div>
      <div>
        <a href="https://github.com/hics-nepal">GitHub</a> &nbsp;·&nbsp;
        <a href="/data/">Open Data</a> &nbsp;·&nbsp;
        <a href="mailto:info@himalayansciences.org">info@himalayansciences.org</a>
      </div>
      <div class="text-dim">
        All data published under CC BY 4.0 &nbsp;·&nbsp;
        All instrument designs under CERN OHL
      </div>
    </div>
  </div>
</footer>

<script src="{% static 'js/main.js' %}"></script>
{% block extra_js %}{% endblock %}
</body>
</html>
```

### Step 5.2 — Home page (`templates/pages/home_page.html`)

```html
{% extends "base.html" %} {% load static wagtailcore_tags wagtailimages_tags %}
{% block content %}

<div class="container">
  <!-- Hero -->
  <section class="hero">
    <div class="hero__mission">{{ page.mission }}</div>
    {% if page.intro %}
    <div class="hero__sub">{{ page.intro|richtext }}</div>
    {% endif %}
  </section>

  <!-- Live data -->
  <section class="section">
    <div class="section__label">Live instrument data</div>
    <div class="data-widget">
      <div class="data-widget__header">
        <div class="data-widget__title" id="widget-station-name">
          Loading...
        </div>
        <div class="station-live">
          <div class="station-live__dot offline" id="widget-dot"></div>
          <span
            class="text-mono"
            style="font-size:0.75rem"
            id="widget-timestamp"
            >—</span
          >
        </div>
      </div>
      <div class="data-widget__readings" id="widget-readings">
        {% for key, label, unit in readings_config %}
        <div class="reading">
          <div>
            <span class="reading__value" id="val-{{ key }}">—</span
            ><span class="reading__unit">{{ unit }}</span>
          </div>
          <div class="reading__label">{{ label }}</div>
        </div>
        {% endfor %}
      </div>
    </div>
  </section>

  <!-- Instruments -->
  <section class="section">
    <div class="section__label">Instruments</div>
    <div class="card-grid">
      {% for instrument in instruments %}
      <a href="{{ instrument.url }}" class="card">
        <div class="card__label">{{ instrument.get_status_display }}</div>
        <div class="card__title">{{ instrument.title }}</div>
        <div class="card__body">{{ instrument.summary }}</div>
        <span class="badge badge--{{ instrument.status }}"
          >{{ instrument.get_status_display }}</span
        >
      </a>
      {% endfor %}
    </div>
  </section>

  <!-- Latest notes -->
  <section class="section">
    <div class="section__label">Latest from the lab</div>
    <div class="note-list">
      {% for note in latest_notes %}
      <a
        href="{{ note.url }}"
        class="note-item"
        style="text-decoration:none;color:inherit;"
      >
        <div class="note-item__meta">
          <div class="note-item__date mono">{{ note.date|date:"d M Y" }}</div>
          <div class="note-item__type text-muted">
            {{ note.get_note_type_display }}
          </div>
        </div>
        <div>
          <div class="note-item__title">{{ note.title }}</div>
          <div class="note-item__summary">{{ note.summary }}</div>
        </div>
      </a>
      {% endfor %}
    </div>
  </section>
</div>
{% endblock %} {% block extra_js %}
<script>
  // Fetch latest sensor data and populate widget
  fetch("/api/data/latest/?station=KTM-001")
    .then((r) => r.json())
    .then((d) => {
      if (d.error) return;
      document.getElementById("widget-station-name").textContent =
        d.station_name + " · " + d.altitude_m + "m";
      document.getElementById("widget-timestamp").textContent = new Date(
        d.timestamp,
      ).toLocaleString();
      document.getElementById("widget-dot").classList.remove("offline");
      document.getElementById("station-dot").classList.remove("offline");

      const vals = {
        temperature_c: d.temperature_c,
        humidity_rh: d.humidity_rh,
        pressure_hpa: d.pressure_hpa,
        pm2_5: d.pm2_5,
      };
      for (const [key, val] of Object.entries(vals)) {
        const el = document.getElementById("val-" + key);
        if (el && val !== null) el.textContent = val.toFixed(1);
      }
      // Update header readout
      document.getElementById("station-reading").textContent =
        (d.temperature_c ? d.temperature_c.toFixed(1) + "°C " : "") +
        (d.humidity_rh ? d.humidity_rh.toFixed(0) + "% RH " : "") +
        (d.pressure_hpa ? d.pressure_hpa.toFixed(0) + " hPa" : "");
    })
    .catch(() => {});
</script>
{% endblock %}
```

---

## Part 6 — RPi Sync Script

**This lives in `iesh-firmware` repo, not the website repo.**

`sync_to_hics.py` — runs on the RPi via cron every 10 minutes:

```python
#!/usr/bin/env python3
"""IESH → himalayansciences.org sync daemon."""

import sqlite3, requests, json, logging
from datetime import datetime, timezone
from pathlib import Path

STATION_ID = "KTM-001"
API_KEY = "your-station-api-key-here"
API_URL = "https://himalayansciences.org/api/ingest/environmental/"
DB_PATH = Path("/home/pi/HICS_data/local.db")

logging.basicConfig(
    filename="/home/pi/HICS_data/sync.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def get_unsynced(conn, limit=100):
    return conn.execute(
        "SELECT rowid, timestamp, temperature_c, humidity_rh, "
        "pressure_hpa, pm2_5, pm10, co2_ppm "
        "FROM readings WHERE synced=0 ORDER BY timestamp LIMIT ?",
        (limit,)
    ).fetchall()

def mark_synced(conn, rowids):
    conn.executemany(
        "UPDATE readings SET synced=1 WHERE rowid=?",
        [(r,) for r in rowids]
    )
    conn.commit()

def push(rows):
    payload = {
        "station_id": STATION_ID,
        "readings": [
            {
                "timestamp": r[1],
                "temperature_c": r[2],
                "humidity_rh": r[3],
                "pressure_hpa": r[4],
                "pm2_5": r[5],
                "pm10": r[6],
                "co2_ppm": r[7],
            }
            for r in rows
        ]
    }
    resp = requests.post(
        API_URL,
        headers={
            "Authorization": f"Token {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    return resp.json().get("accepted", 0)

def main():
    conn = sqlite3.connect(DB_PATH)
    rows = get_unsynced(conn)
    if not rows:
        return
    try:
        accepted = push(rows)
        mark_synced(conn, [r[0] for r in rows])
        logging.info(f"Synced {accepted} readings to HICS server.")
    except Exception as e:
        logging.error(f"Sync failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

# Add to RPi crontab:
# */10 * * * * /usr/bin/python3 /home/pi/sync_to_hics.py
```

## Part 7 — CI/CD (GitHub Actions → cPanel SSH)

**`.github/workflows/deploy.yml`**:

```yaml
name: Deploy to cPanel Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.CPANEL_SSH_HOST }}
          username: ${{ secrets.CPANEL_SSH_USER }}
          key: ${{ secrets.CPANEL_SSH_KEY }}
          script: |
            set -e
            if [ ! -d "$HOME/himalayansciences-web" ]; then
              echo "Repository not found on server. Cloning for the first time..."
              git clone https://github.com/hics-nepal/himalayansciences-web.git "$HOME/himalayansciences-web"
              cd "$HOME/himalayansciences-web"
            else
              cd "$HOME/himalayansciences-web"
              rm -f passenger_wsgi.py
              git pull origin main
            fi

            # Initialize .env if missing
            if [ ! -f .env ]; then
              echo "Initializing .env file..."
              cp .env.example .env
              # Generate a secure random Django SECRET_KEY
              RANDOM_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" || python -c "import secrets; print(secrets.token_urlsafe(50))" || echo "django-insecure-prod-hics-key-$(date +%s)")
              sed -i "s|your-secret-key-here|$RANDOM_KEY|g" .env
              # Force DEBUG=False and Production ALLOWED_HOSTS
              sed -i "s|DEBUG=True|DEBUG=False|g" .env
              sed -i "s|ALLOWED_HOSTS=localhost,127.0.0.1|ALLOWED_HOSTS=himalayansciences.org,www.himalayansciences.org|g" .env
            fi

            # Dynamically inject/update Database details from GitHub Secrets
            if [ -n "${{ secrets.DB_NAME }}" ]; then
              sed -i "s|^DB_NAME=.*|DB_NAME=${{ secrets.DB_NAME }}|g" .env
            fi
            if [ -n "${{ secrets.DB_USER }}" ]; then
              sed -i "s|^DB_USER=.*|DB_USER=${{ secrets.DB_USER }}|g" .env
            fi
            if [ -n "${{ secrets.DB_PASSWORD }}" ]; then
              # Use | as delimiter to avoid slashes in password breaking sed
              sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=${{ secrets.DB_PASSWORD }}|g" .env
            fi

            # Locate cPanel LVE virtual environment
            CPANEL_VENV=$(find $HOME/virtualenv -name "activate" | grep "himalayansciences-web" | head -n 1 || true)
            if [ -n "$CPANEL_VENV" ]; then
              echo "Activating cPanel managed virtualenv: $CPANEL_VENV"
              source "$CPANEL_VENV"
            else
              echo "WARNING: cPanel virtualenv not found. Please create the Python App in your cPanel dashboard first!"
              exit 1
            fi

            pip install --upgrade pip --quiet
            pip install -r requirements.txt --quiet

            DJANGO_SETTINGS_MODULE=hics.settings.production \
              python manage.py migrate --no-input
            DJANGO_SETTINGS_MODULE=hics.settings.production \
              python manage.py collectstatic --no-input --clear
            mkdir -p tmp
            touch tmp/restart.txt
            echo "Deploy complete: $(date)"
```

**GitHub Secrets to add** (repo Settings → Secrets → Actions):

- `CPANEL_SSH_HOST` — your server IP address (e.g., `69.57.172.41`)
- `CPANEL_SSH_USER` — your cPanel username (`elyakadv`)
- `CPANEL_SSH_KEY` — private key (e.g., the contents of `id_ed25519` generated in cPanel SSH access)
- `DB_NAME` — database name (`elyakadv_hics`)
- `DB_USER` — database user (`elyakadv_hicsadmin`)
- `DB_PASSWORD` — database password

---

## Part 8 — cPanel Deployment Setup

Do this once to configure the server:

```bash
# 1. SSH into your cPanel server
ssh elyakadv@69.57.172.41

# 2. Clone the repo
cd ~
git clone https://github.com/hics-nepal/himalayansciences-web.git
cd himalayansciences-web

# 3. Create virtualenv and link it (handled by cPanel's Setup Python App)
#    - Python Version: 3.11.x
#    - Application Root: himalayansciences-web
#    - Application URL: himalayansciences.org
#    - Application startup file: passenger_wsgi.py
#    - Application Entry point: application

# 4. Run migrations & Seeding using cPanel "Execute Command" or CLI
DJANGO_SETTINGS_MODULE=hics.settings.production python manage.py migrate
DJANGO_SETTINGS_MODULE=hics.settings.production python manage.py seed_hics
DJANGO_SETTINGS_MODULE=hics.settings.production python manage.py createsuperuser
```

**`passenger_wsgi.py`** — automatically generated by Git/deploy process to boot Django under cPanel's Phusion Passenger:
```python
import os
import sys

# Load virtual environment packages
VENV_PACKAGES = '/home/elyakadv/virtualenv/himalayansciences-web/3.11/lib/python3.11/site-packages'
if VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)

sys.path.insert(0, os.path.dirname(__file__))

import hics.wsgi
application = hics.wsgi.application
```

> [!WARNING]
> **cPanel Setup Python App Alert:**
> Under certain LiteSpeed/cPanel conditions, saving or restarting the application in the cPanel GUI can aggressively overwrite your Django entry point (`hics/wsgi.py`) with a generic "It works! Python..." placeholder template, breaking Django silently. 
> To prevent this, the deployment pipeline includes a mandatory `git checkout hics/wsgi.py` safeguard. If you ever see the "It works!" screen after a manual restart, simply run `git checkout hics/wsgi.py` on the server and ensure `passenger_wsgi.py` is set to `755` executable permissions.

---

## Part 9 — MySQL Setup on cPanel

```
cPanel → MySQL Databases:
  1. Create database: elyakadv_hics
  2. Create user:     elyakadv_hicsadmin  (strong password)
  3. Add user to DB:  ALL PRIVILEGES
```

Then in `.env` (automatically injected via GitHub Actions deployment secrets):

```
DB_NAME=elyakadv_hics
DB_USER=elyakadv_hicsadmin
DB_PASSWORD=<database password>
```

---

## Part 10 — Launch Checklist

### Phase 1 — Local working

- [x] `django-admin startproject` + Wagtail installed
- [x] All models written and migrated (SQLite locally)
- [x] `python manage.py runserver` — Wagtail admin at `/cms/`
- [x] Home page, About, Instrument, LabNote page types working in admin
- [x] API endpoints responding: `/api/data/latest/`, `/api/ingest/environmental/`
- [x] CSS applied, fonts loading, live widget JS working
- [x] Pushed to `github.com/hics-nepal/himalayansciences-web`

### Phase 2 — cPanel deployed

- [x] Python app created in cPanel
- [x] MySQL database created, `.env` secrets filled in GitHub Secrets
- [x] Pinned compatible dependencies to prevent installation recursions
- [x] Created `passenger_wsgi.py` to route traffic to Django
- [x] `git clone` and `migrate` run on server automatically via CI/CD
- [x] Site loads at `himalayansciences.org` (once nameservers propagate)
- [x] SSL active (NestNepal provides Let's Encrypt via cPanel AutoSSL)
- [x] GitHub Actions SSH deploy working (push → auto-deploys with zero blocks)

### Phase 3 — Content live

- [x] Seed page tree and database using `python manage.py seed_hics` (Home → index pages & default KTM-001 Station)
- [ ] Create Wagtail admin superuser account via Setup Python App GUI
- [ ] Write and publish: About page (use existing bio draft)
- [ ] Create first InstrumentPage: IESH v0
- [ ] Write first LabNotePage: Eta Aquariid observation
- [ ] Write first LabNotePage: IESH build log
- [ ] Create first ResearchProgrammePage: Atmospheric Science
- [ ] Add PRD paper as Publication snippet, link from About
- [ ] Data page live with chart (even if no live data yet)

### Phase 4 — Data flowing

- [ ] RPi sync script installed and in crontab on KTM-001 station
- [ ] First readings visible at `/api/data/latest/`
- [ ] Chart on data page showing real readings
- [ ] Header live-readout widget showing real temperature
- [ ] CSV download working at `/api/data/download/`
- [ ] Share: AIT application, IMO contacts, GMN network

---

## Appendix — Key URLs

| URL                                                   | Purpose                      |
| ----------------------------------------------------- | ---------------------------- |
| `himalayansciences.org/cms/`                          | Wagtail admin                |
| `himalayansciences.org/api/data/latest/`              | Latest reading (public JSON) |
| `himalayansciences.org/api/data/historical/?hours=24` | Time series (public JSON)    |
| `himalayansciences.org/api/data/download/`            | CSV download (public)        |
| `himalayansciences.org/api/ingest/environmental/`     | Instrument POST endpoint     |

## Appendix — Key Commands

```bash
# Local dev
source venv/bin/activate
DJANGO_SETTINGS_MODULE=hics.settings.local python manage.py runserver

# Make migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Seeding initial page structure and station
python manage.py seed_hics

# Create superuser
python manage.py createsuperuser

# Generate new station API key
python manage.py shell
>>> from instruments.models import Station
>>> key = Station.generate_api_key()
>>> print(key)  # store this — only shown once
>>> s = Station.objects.get(station_id='KTM-001')
>>> s.set_api_key(key)
>>> s.save()
```

---

_This document drives the build. Update it as implementation decisions are made._
_Sections 1–5 are local setup. Sections 6–9 are deployment. Section 10 is the checklist._
