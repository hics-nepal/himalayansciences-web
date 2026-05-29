from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.blocks import (
    RichTextBlock, CharBlock,
    TextBlock, StructBlock, URLBlock, ListBlock
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.snippets.models import register_snippet
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

    def __str__(self):
        return f"{self.authors.split(',')[0]} et al. ({self.year})"


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


BODY_BLOCKS = [
    ('text', RichTextBlock(features=[
        'h2', 'h3', 'bold', 'italic', 'link', 'ol', 'ul', 'blockquote', 'superscript'
    ])),
    ('image', ImageChooserBlock()),
    ('sensor_chart', SensorChartBlock()),
    ('coordinates', CoordinatesBlock()),
    ('code', CodeBlock()),
    ('document', DocumentChooserBlock()),
    ('pull_quote', TextBlock()),
]


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
        # Config for the live data widget slots
        ctx['readings_config'] = [
            ('temperature_c', 'Temperature', '°C'),
            ('humidity_rh', 'Humidity', '% RH'),
            ('pressure_hpa', 'Pressure', 'hPa'),
            ('pm2_5', 'PM 2.5', 'µg/m³'),
        ]
        return ctx


class AboutPage(Page):
    intro = RichTextField()
    body = StreamField(BODY_BLOCKS, use_json_field=True, blank=True)
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
        choices=[('active', 'Active'), ('planned', 'Planned'), ('paused', 'Paused')],
        default='planned')
    summary = models.TextField(max_length=300,
        help_text="One paragraph, shown on index page.")
    body = StreamField(BODY_BLOCKS, use_json_field=True, blank=True)
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
    body = StreamField(BODY_BLOCKS, use_json_field=True, blank=True)
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
    body = StreamField(BODY_BLOCKS, use_json_field=True, blank=True)
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
