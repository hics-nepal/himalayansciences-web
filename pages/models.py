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


class ImageWithCaptionBlock(StructBlock):
    """Image with optional caption and sizing control."""
    image = ImageChooserBlock()
    caption = CharBlock(required=False)
    size = CharBlock(default='full',
        help_text='full | content | small')

    class Meta:
        icon = 'image'
        label = 'Image with Caption'
        template = 'pages/blocks/image_caption.html'


class SectionHeadingBlock(StructBlock):
    """Section label + heading, matching the HICS design system."""
    label = CharBlock(required=False,
        help_text='Small uppercase label above heading (e.g. "Research")')
    heading = CharBlock()

    class Meta:
        icon = 'title'
        label = 'Section Heading'
        template = 'pages/blocks/section_heading.html'


class CalloutBlock(StructBlock):
    """Highlighted callout box — for key facts, warnings, or notes."""
    CALLOUT_TYPES = [
        ('note', 'Note (blue)'),
        ('key', 'Key Fact (amber)'),
        ('status', 'Status Update (green)'),
        ('warning', 'Warning (red)'),
    ]
    callout_type = CharBlock(default='note',
        help_text='note | key | status | warning')
    title = CharBlock(required=False)
    body = RichTextBlock(features=['bold', 'italic', 'link', 'ul', 'ol'])

    class Meta:
        icon = 'warning'
        label = 'Callout Box'
        template = 'pages/blocks/callout.html'


class StatsRowBlock(StructBlock):
    """Row of key statistics/numbers."""
    stats = ListBlock(StructBlock([
        ('value', CharBlock(help_text='e.g. "8,848" or "24/7"')),
        ('unit', CharBlock(required=False, help_text='e.g. "m" or "hours"')),
        ('label', CharBlock(help_text='e.g. "Maximum altitude"')),
    ]))

    class Meta:
        icon = 'order'
        label = 'Statistics Row'
        template = 'pages/blocks/stats_row.html'


class PersonBlock(StructBlock):
    """Team member or collaborator card."""
    name = CharBlock()
    role = CharBlock(required=False)
    photo = ImageChooserBlock(required=False)
    bio = RichTextBlock(features=['bold', 'italic', 'link'], required=False)

    class Meta:
        icon = 'user'
        label = 'Person Card'
        template = 'pages/blocks/person.html'


class AccordionBlock(StructBlock):
    """Expandable FAQ or details section."""
    items = ListBlock(StructBlock([
        ('question', CharBlock()),
        ('answer', RichTextBlock(features=['bold', 'italic', 'link', 'ul', 'ol'])),
    ]))

    class Meta:
        icon = 'list-ul'
        label = 'Accordion / FAQ'
        template = 'pages/blocks/accordion.html'


class PullQuoteBlock(StructBlock):
    """Styled pull quote with optional attribution."""
    quote = TextBlock()
    attribution = CharBlock(required=False)

    class Meta:
        icon = 'openquote'
        label = 'Pull Quote'
        template = 'pages/blocks/pull_quote.html'


BODY_BLOCKS = [
    ('text', RichTextBlock(features=[
        'h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul',
        'blockquote', 'superscript', 'hr',
    ])),
    ('image', ImageWithCaptionBlock()),
    ('section_heading', SectionHeadingBlock()),
    ('callout', CalloutBlock()),
    ('stats', StatsRowBlock()),
    ('person', PersonBlock()),
    ('accordion', AccordionBlock()),
    ('pull_quote', PullQuoteBlock()),
    ('sensor_chart', SensorChartBlock()),
    ('coordinates', CoordinatesBlock()),
    ('code', CodeBlock()),
    ('document', DocumentChooserBlock()),
    ('raw_image', ImageChooserBlock()),
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
        ('glaciology', 'Glaciology and Cryosphere'),
        ('computational', 'Computational Science'),
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
    form_title = models.CharField(max_length=200, default='Send a direct message', blank=True)
    success_message = models.TextField(default='Thank you! Your message has been sent successfully. We will get back to you shortly.', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('email_research'),
        FieldPanel('email_education'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('form_title'),
            FieldPanel('success_message'),
        ], heading="Direct Contact Form Settings"),
    ]

    def serve(self, request):
        if request.method == 'POST':
            from django.core.mail import send_mail
            from django.shortcuts import render
            
            category = request.POST.get('category', 'General Enquiry')
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            
            # Simple validation
            if not name or not email or not message:
                errors = "Please fill in all required fields (Name, Email, Message)."
                return render(request, self.get_template(request), {
                    'page': self,
                    'errors': errors,
                    'form_data': request.POST
                })
            
            # Determine destination email
            to_email = self.email_research or 'info@himalayansciences.org'
            if category == 'Education' and self.email_education:
                to_email = self.email_education
            
            # Construct email
            email_subject = f"HICS Contact Form: [{category}] {subject or 'No Subject'}"
            email_body = f"Name: {name}\nEmail: {email}\nCategory: {category}\nSubject: {subject}\n\nMessage:\n{message}"
            
            try:
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email='no-reply@himalayansciences.org',
                    recipient_list=[to_email],
                    fail_silently=False,
                )
                success = True
            except Exception as e:
                errors = f"Failed to send email: {str(e)}"
                return render(request, self.get_template(request), {
                    'page': self,
                    'errors': errors,
                    'form_data': request.POST
                })
            
            return render(request, self.get_template(request), {
                'page': self,
                'success': True
            })
            
        return super().serve(request)


class EducationIndexPage(Page):
    """Index page for structured education programmes."""
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel('intro')]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['programmes'] = EducationProgrammePage.objects.live().child_of(self)
        return ctx


class EducationProgrammePage(Page):
    """Individual education programme page (residency, fellowship, camp, etc.)."""
    PROGRAMME_CHOICES = [
        ('residency', 'School Science Residency'),
        ('fellowship', 'Youth Research Fellowship'),
        ('camp', 'Annual Science Camp'),
        ('teachers', 'Teacher Professional Development'),
        ('computing', 'Scientific Computing Courses'),
        ('public', 'Public Science Programme'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('planned', 'Planned'),
        ('accepting', 'Accepting Applications'),
    ]
    programme_type = models.CharField(max_length=30, choices=PROGRAMME_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    summary = models.TextField(max_length=400,
        help_text="Short description shown on index page.")
    body = StreamField(BODY_BLOCKS, use_json_field=True, blank=True)
    target_audience = models.CharField(max_length=200, blank=True,
        help_text="e.g. 'High school students, Grades 9-11'")
    contact_email = models.EmailField(default='info@himalayansciences.org')
    contact_subject = models.CharField(max_length=200, blank=True,
        help_text="Pre-filled email subject line.")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('programme_type'),
            FieldPanel('status'),
            FieldPanel('target_audience'),
        ], heading='Programme Details'),
        FieldPanel('summary'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('contact_email'),
            FieldPanel('contact_subject'),
        ], heading='Contact'),
    ]


class LearnIndexPage(Page):
    """Index page for free learning resources."""
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel('intro')]


class OpenKnowledgePage(Page):
    """Open Knowledge overview page — gateway to /data/ and /learn/."""
    intro = RichTextField(blank=True)
    body = StreamField(BODY_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
