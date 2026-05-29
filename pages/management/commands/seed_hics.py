import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page
from pages.models import (
    HomePage, AboutPage, ResearchIndexPage, ResearchProgrammePage,
    InstrumentIndexPage, InstrumentPage, DataPage, LabNoteIndexPage, ContactPage
)
from instruments.models import Station


class Command(BaseCommand):
    help = "Seeds default HICS Wagtail pages, stations, and index structures."

    def handle(self, *args, **options):
        self.stdout.write("Starting HICS database seeding...")

        # 1. Update the default HomePage
        try:
            home_page = HomePage.objects.first()
            if home_page:
                home_page.title = "Himalayan Institute for Contextual Sciences"
                home_page.tagline = "Science rooted in place. Data open to all."
                home_page.mission = "HICS conducts high-altitude physics, meteor astronomy, and environmental sensing to produce open-access contextual scientific research in the Himalayas."
                home_page.intro = "<p>Based in Kathmandu, Nepal, we build custom open-source scientific instruments (IESH) to monitor cosmic rays, air quality, and atmospheric parameters.</p>"
                home_page.save()
                self.stdout.write(self.style.SUCCESS("Updated default HomePage."))
            else:
                self.stdout.write(self.style.WARNING("HomePage not found. Please run migrations first."))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error finding HomePage: {e}"))
            return

        # 2. Add Index Pages if they don't exist
        # Helper to get or create child pages
        def get_or_create_child_page(parent, page_class, slug, title, **kwargs):
            existing_page = page_class.objects.filter(slug=slug).first()
            if existing_page:
                self.stdout.write(f"Page '{title}' already exists.")
                return existing_page
            
            child = page_class(
                title=title,
                slug=slug,
                **kwargs
            )
            parent.add_child(instance=child)
            child.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"Created and published '{title}' page."))
            return child

        # About Page
        about = get_or_create_child_page(
            home_page, AboutPage, "about", "About Us",
            intro="<p>Welcome to HICS. We are a team of dedicated researchers, engineers, and educators studying the high-altitude environment of the Himalayas.</p>",
            registration_info="<p>The Himalayan Institute for Contextual Sciences is registered in Kathmandu, Nepal as an independent research organisation.</p>"
        )

        # Research Index Page
        research_index = get_or_create_child_page(
            home_page, ResearchIndexPage, "research", "Research",
            intro="<p>Our research focuses on context-specific, high-altitude science that is often overlooked by global models. All of our datasets are open to the public.</p>"
        )

        # Research Programme: Atmospheric Science
        get_or_create_child_page(
            research_index, ResearchProgrammePage, "atmospheric-science", "Atmospheric Science",
            programme_type="atmospheric",
            status="active",
            summary="Monitoring atmospheric parameters, particulate matter (PM2.5), and greenhouse gases in the Kathmandu Valley.",
            body=[]
        )

        # Instruments Index Page
        instruments_index = get_or_create_child_page(
            home_page, InstrumentIndexPage, "instruments", "Instruments",
            intro="<p>We build our own scientific hardware under the CERN Open Hardware Licence. This ensures our research is fully reproducible and cost-effective.</p>"
        )

        # Instrument: IESH v0
        get_or_create_child_page(
            instruments_index, InstrumentPage, "iesh-v0", "IESH v0 Station",
            status="active",
            station_id="KTM-001",
            summary="Our first integrated environmental sensing station designed for high-reliability air and weather tracking.",
            what_it_measures="<p>Measures Temperature, Humidity, Barometric Pressure, PM1.0, PM2.5, PM10, and CO2.</p>",
            github_url="https://github.com/hics-nepal"
        )

        # Data Page
        get_or_create_child_page(
            home_page, DataPage, "data", "Live Data",
            intro="<p>Explore real-time raw data streams and historical archives from our deployed observation stations in Nepal.</p>",
            api_docs="<p>You can access real-time JSON data at <code>/api/data/latest/</code> and download CSV records at <code>/api/data/download/</code>.</p>"
        )

        # Notes (Blog) Index Page
        get_or_create_child_page(
            home_page, LabNoteIndexPage, "notes", "Lab Notes",
            intro="<p>Dispatches from the field, experiment logs, and research updates directly from our scientists.</p>"
        )

        # Contact Page
        get_or_create_child_page(
            home_page, ContactPage, "contact", "Contact",
            intro="<p>Get in touch with us regarding research partnerships, open data, or instrument builds.</p>",
            email_research="info@himalayansciences.org",
            email_education="edu@himalayansciences.org"
        )

        # 3. Create default Station KTM-001
        station, created = Station.objects.get_or_create(
            station_id="KTM-001",
            defaults={
                "name": "Kathmandu Central Station",
                "description": "Primary multi-sensor atmospheric and cosmic ray tracking node located at HICS HQ.",
                "latitude": 27.7172,
                "longitude": 85.3240,
                "altitude_m": 1400.0,
                "location_name": "Kathmandu HQ",
                "status": "active"
            }
        )

        if created:
            # Generate and print a new API Key for the station
            api_key = Station.generate_api_key()
            station.set_api_key(api_key)
            station.save()
            self.stdout.write(self.style.SUCCESS(f"Created Station KTM-001 with API Key: {api_key}"))
            self.stdout.write(self.style.WARNING("!!! SAVE THIS KEY NOW - IT WILL NOT BE SHOWN AGAIN !!!"))
        else:
            self.stdout.write("Station KTM-001 already exists.")

        self.stdout.write(self.style.SUCCESS("HICS Database Seeding Complete!"))
