import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page, Site
from pages.models import (
    HomePage, AboutPage, ResearchIndexPage, ResearchProgrammePage,
    InstrumentIndexPage, InstrumentPage, DataPage, LabNoteIndexPage, ContactPage,
    EducationIndexPage, EducationProgrammePage, LearnIndexPage, OpenKnowledgePage
)
from instruments.models import Station


class Command(BaseCommand):
    help = "Seeds default HICS Wagtail pages, stations, and index structures."

    def handle(self, *args, **options):
        self.stdout.write("Starting HICS database seeding...")

        # 1. Get or Create the custom HomePage under the Wagtail Root node
        try:
            home_page = HomePage.objects.first()
            if not home_page:
                self.stdout.write("Custom HomePage not found. Creating it under the Wagtail Root node...")
                # Get the absolute Root page node (depth 1)
                root_page = Page.get_first_root_node()
                if not root_page:
                    root_page = Page.objects.get(id=1)
                
                # Check for any default Wagtail homepages at depth 2 (slug "home") and remove them
                default_home = Page.objects.filter(depth=2).first()
                if default_home:
                    self.stdout.write(f"Removing default Wagtail page '{default_home.title}' to prevent conflicts.")
                    default_home.delete()

                # Create the custom HomePage instance
                home_page = HomePage(
                    title="Himalayan Institute for Contextual Sciences",
                    slug="home",
                    tagline="Contextual Science. Open Data. Real-World Learning.",
                    mission="HICS is an independent research, instrumentation, and learning institution based in Kathmandu, Nepal. We work across four domains — Research, Instrumentation, Education, and Open Knowledge — building the translational infrastructure that makes doing serious science in Nepal possible.",
                    intro="<p>We are built on a single organising principle: that Nepal's geography, ecology, seismology, atmosphere, and cultural knowledge are not obstacles to doing serious science — they are the material. Science done here should be about here.</p>"
                )
                root_page.add_child(instance=home_page)
                home_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS("Created and published custom HomePage."))
            else:
                # HomePage already exists - just update its default details
                home_page.title = "Himalayan Institute for Contextual Sciences"
                home_page.tagline = "Contextual Science. Open Data. Real-World Learning."
                home_page.mission = "HICS is an independent research, instrumentation, and learning institution based in Kathmandu, Nepal. We work across four domains — Research, Instrumentation, Education, and Open Knowledge — building the translational infrastructure that makes doing serious science in Nepal possible."
                home_page.intro = "<p>We are built on a single organising principle: that Nepal's geography, ecology, seismology, atmosphere, and cultural knowledge are not obstacles to doing serious science — they are the material. Science done here should be about here.</p>"
                home_page.save()
                self.stdout.write(self.style.SUCCESS("Updated default HomePage."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error initializing HomePage: {e}"))
            return

        # Update Wagtail Site object to point to our custom HomePage
        try:
            site = Site.objects.first()
            if site:
                site.root_page = home_page
                site.hostname = "himalayansciences.org"
                site.port = 443
                site.site_name = "Himalayan Institute for Contextual Sciences"
                site.save()
                self.stdout.write(self.style.SUCCESS("Configured default Wagtail Site to point to our custom HomePage at himalayansciences.org (HTTPS)."))
            else:
                # If no Site object exists, create one
                Site.objects.create(
                    hostname="himalayansciences.org",
                    port=443,
                    site_name="Himalayan Institute for Contextual Sciences",
                    root_page=home_page,
                    is_default_site=True
                )
                self.stdout.write(self.style.SUCCESS("Created and configured default Wagtail Site at himalayansciences.org (HTTPS)."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not configure Wagtail Site: {e}"))

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

        # Education Index Page
        education_index = get_or_create_child_page(
            home_page, EducationIndexPage, "education", "Education Programmes",
            intro="<p>HICS's education programmes bring instruments, data, and real scientific practice directly into schools and communities. Not textbook science — students analyse real data from real instruments collecting real signals from the world around them.</p>"
        )

        # Education Programme: School Residency
        get_or_create_child_page(
            education_index, EducationProgrammePage, "residency", "School Science Residency Programme",
            programme_type="residency",
            status="planned",
            summary="Multi-day visits to schools combining planetarium sessions, instrument workshops, data exploration, and teacher training.",
            target_audience="Schools, primarily outside Kathmandu",
            contact_subject="School residency",
            body=[]
        )

        # Education Programme: Youth Research Fellowship
        get_or_create_child_page(
            education_index, EducationProgrammePage, "fellowship", "Youth Research Fellowship",
            programme_type="fellowship",
            status="planned",
            summary="Full-time 12–24 month research positions for Nepali scientists and engineers. Real research. Real stipend. Real publications.",
            target_audience="Nepali scientists and engineers",
            contact_subject="Fellowship enquiry",
            body=[]
        )

        # Education Programme: Science Camp
        get_or_create_child_page(
            education_index, EducationProgrammePage, "camp", "Annual Science Camp",
            programme_type="camp",
            status="planned",
            summary="Ten-day residential programme for high school students (Grades 9–11) selected from across Nepal. Priority for students from districts outside Kathmandu.",
            target_audience="High school students, Grades 9-11",
            contact_subject="Science camp",
            body=[]
        )

        # Education Programme: Teacher Development
        get_or_create_child_page(
            education_index, EducationProgrammePage, "teachers", "Teacher Professional Development",
            programme_type="teachers",
            status="planned",
            summary="Annual one-week residential intensive. Teachers leave with a working instrument they built, curriculum modules ready to teach, and membership in an ongoing professional community.",
            target_audience="Teachers across Nepal",
            contact_subject="Teacher development",
            body=[]
        )

        # Learn Index Page
        get_or_create_child_page(
            home_page, LearnIndexPage, "learn", "Learning Resources",
            intro="<p>HICS's learning resources are freely available — for teachers, students, and anyone who wants to understand the science behind the instruments and data. Download them, use them, adapt them.</p>"
        )

        # Open Knowledge Page
        get_or_create_child_page(
            home_page, OpenKnowledgePage, "open-knowledge", "Open Knowledge",
            intro="<p>HICS's public outputs exist for the world, not only for HICS's own programmes. All data is open. All instrument designs are open-source. All learning materials are freely available.</p>",
            body=[]
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

