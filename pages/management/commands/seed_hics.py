import os
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from wagtail.models import Page, Site, Locale
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

        # 0. Automatically convert database and tables to utf8mb4 if using MySQL
        if connection.vendor == 'mysql':
            try:
                self.stdout.write("Checking and converting MySQL database and tables to utf8mb4...")
                db_name = connection.settings_dict['NAME']
                with connection.cursor() as cursor:
                    # Convert database charset and collation to support devanagari unicode characters
                    cursor.execute(f"ALTER DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                    
                    # Fetch all tables
                    cursor.execute("SHOW TABLES;")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    # Convert each table
                    for table in tables:
                        try:
                            cursor.execute(f"ALTER TABLE `{table}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                        except Exception as table_err:
                            self.stdout.write(self.style.WARNING(f"Could not convert table {table}: {table_err}"))
                            
                self.stdout.write(self.style.SUCCESS("Database and tables successfully converted to utf8mb4 unicode!"))
            except Exception as db_err:
                self.stdout.write(self.style.WARNING(f"Database unicode conversion skipped/failed: {db_err}"))

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

        # 4. Automatically synchronize and build the translation page trees
        try:
            self.stdout.write("Synchronizing page translation trees for 'ne' (Nepali) locale...")
            ne_locale, _ = Locale.objects.get_or_create(language_code='ne')
            from wagtail_localize.operations import translate_object
            
            sync_count = 0
            for p in Page.objects.all():
                if p.depth > 1:
                    # Skip pages that already have a translation in the database
                    if not p.get_translations().filter(locale=ne_locale).exists():
                        try:
                            translate_object(p, [ne_locale])
                            sync_count += 1
                        except Exception as translation_err:
                            self.stdout.write(self.style.WARNING(f"Skipped translation clone for '{p.title}': {translation_err}"))
            
            self.stdout.write(self.style.SUCCESS(f"Multilingual synchronization complete! Cloned {sync_count} pages to 'ne' tree."))

            # Automatically populate default translations for Homepage, About Page, and Contact Page in Nepali locale
            self.stdout.write("Populating official Nepali translation copy inside the database...")
            ne_home = HomePage.objects.filter(locale=ne_locale).first()
            if ne_home:
                modified = False
                if ne_home.title == "Himalayan Institute for Contextual Sciences" or not ne_home.title or "?" in str(ne_home.title):
                    ne_home.title = "हिमालयन इन्स्टिच्युट फर कन्टेक्सचुअल साइन्सेस"
                    modified = True
                if ne_home.tagline == "Contextual Science. Open Data. Real-World Learning." or not ne_home.tagline or "?" in str(ne_home.tagline):
                    ne_home.tagline = "सान्दर्भिक विज्ञान। खुला तथ्याङ्क। स्थलगत सिकाइ।"
                    modified = True
                if "HICS is an independent research" in ne_home.mission or "नेपालमा आधारित" in ne_home.mission or "नेपालमा स्थापित" in ne_home.mission or not ne_home.mission or "?" in str(ne_home.mission):
                    ne_home.mission = "नेपालमा स्थापित, HICS एक स्वतन्त्र अनुसन्धान, वैज्ञानिक उपकरण निर्माण, र स्थलगत सिकाइ प्रवर्द्धन गर्ने संस्था हो। हामी यहाँको विशिष्ट भूगोल र परिवेश, हिमाल माथिको वायुमण्डल, हाम्रा सहर मुनिको भौगर्भिक अवस्था र उच्च हिमाली भेगका समुदायहरूको गहन अध्ययन गर्न वैज्ञानिक प्रविधि र उपकरणहरू विकास गर्छौं, तथ्याङ्क सङ्कलन गर्छौं र खुला विज्ञानको प्रवर्द्धन गर्छौं।"
                    modified = True
                if "We are built on a" in str(ne_home.intro) or not ne_home.intro or "?" in str(ne_home.intro):
                    ne_home.intro = "<p>हामी एउटा प्रमुख सिद्धान्तमा आधारित छौं: नेपालको भूगोल, पारिस्थितिक प्रणाली, भूकम्प विज्ञान, वायुमण्डल, र सांस्कृतिक ज्ञान गम्भीर विज्ञान गर्नका लागि अवरोध होइनन् — बरु यिनीहरू नै विज्ञानका मूल आधार हुन्। यहाँ गरिने विज्ञान, यहाँकै बारेमा हुनुपर्छ।</p>"
                    modified = True
                
                if modified:
                    ne_home.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Homepage translation!"))
                else:
                    self.stdout.write("Nepali Homepage was modified in Wagtail Admin. Preserving your edits.")

            ne_about = AboutPage.objects.filter(locale=ne_locale).first()
            if ne_about:
                modified = False
                if ne_about.title == "About Us" or ne_about.title == "About" or not ne_about.title or "?" in str(ne_about.title):
                    ne_about.title = "हाम्रो बारेमा"
                    modified = True
                if "Welcome to HICS" in str(ne_about.intro) or "नेपालको विशिष्ट भौगोलिक उचाइ" in str(ne_about.intro) or not ne_about.intro or "?" in str(ne_about.intro):
                    ne_about.intro = "<p>हामी नेपालको विशिष्ट भौगोलिक उचाइ र वातावरणीय विविधतालाई सम्बोधन गर्ने वैज्ञानिक अनुसन्धान र खुला-स्रोत प्रविधिको विकासमा समर्पित छौं।</p>"
                    modified = True
                if "registered in Kathmandu" in str(ne_about.registration_info) or not ne_about.registration_info or "?" in str(ne_about.registration_info):
                    ne_about.registration_info = "<p>हिमालयन इन्स्टिच्युट फर कन्टेक्सचुअल साइन्सेस प्रा. लि. नेपालमा कम्पनी ऐन २०६३ (२००६) अन्तर्गत एक स्वतन्त्र अनुसन्धान संस्थाको रूपमा दर्ता गरिएको छ।</p>"
                    modified = True
                
                if modified:
                    ne_about.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali AboutPage translation!"))
                else:
                    self.stdout.write("Nepali AboutPage was modified in Wagtail Admin. Preserving your edits.")

            ne_contact = ContactPage.objects.filter(locale=ne_locale).first()
            if ne_contact:
                modified = False
                if ne_contact.title == "Contact" or not ne_contact.title or "?" in str(ne_contact.title):
                    ne_contact.title = "सम्पर्क"
                    modified = True
                if "Get in touch" in str(ne_contact.intro) or "साझेदारी" in str(ne_contact.intro) or not ne_contact.intro or "?" in str(ne_contact.intro):
                    ne_contact.intro = "<p>वैज्ञानिक अनुसन्धान साझेदारी, खुला तथ्याङ्कको पहुँच, वा उपकरण निर्माण सम्बन्धी सहकार्यका लागि हामीलाई सम्पर्क गर्नुहोस्।</p>"
                    modified = True
                if "Send a direct message" in ne_contact.form_title or not ne_contact.form_title or "?" in str(ne_contact.form_title):
                    ne_contact.form_title = "हामीलाई प्रत्यक्ष सन्देश पठाउनुहोस्"
                    modified = True
                if "Thank you" in str(ne_contact.success_message) or "प्राप्त भएको छ" in str(ne_contact.success_message) or not ne_contact.success_message or "?" in str(ne_contact.success_message):
                    ne_contact.success_message = "तपाईंको सन्देश सफलतापूर्वक प्राप्त भएको छ। हामी चाँडै नै तपाईंसँग सम्पर्क स्थापित गर्नेछौं।"
                    modified = True
                
                if modified:
                    ne_contact.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali ContactPage translation!"))
                else:
                    self.stdout.write("Nepali ContactPage was modified in Wagtail Admin. Preserving your edits.")

            # 5. Populate default translations for remaining index pages in Nepali locale
            ne_research = ResearchIndexPage.objects.filter(locale=ne_locale).first()
            if ne_research:
                modified = False
                if ne_research.title == "Research" or not ne_research.title or "?" in str(ne_research.title):
                    ne_research.title = "अनुसन्धान"
                    modified = True
                if "Our research focuses" in str(ne_research.intro) or "हाम्रो अनुसन्धान" in str(ne_research.intro) or not ne_research.intro or "?" in str(ne_research.intro):
                    ne_research.intro = "<p>हाम्रो अनुसन्धान विश्वव्यापी मोडेलहरूले प्रायः बेवास्ता गर्ने स्थानीय विशिष्ट र उच्च हिमाली विज्ञानमा केन्द्रित छ। हाम्रा सबै तथ्याङ्क सेटहरू सार्वजनिक रूपमा खुला छन्।</p>"
                    modified = True
                if modified:
                    ne_research.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali ResearchIndexPage translation!"))

            ne_instruments = InstrumentIndexPage.objects.filter(locale=ne_locale).first()
            if ne_instruments:
                modified = False
                if ne_instruments.title == "Instruments" or not ne_instruments.title or "?" in str(ne_instruments.title):
                    ne_instruments.title = "वैज्ञानिक उपकरणहरू"
                    modified = True
                if "We build our own" in str(ne_instruments.intro) or "CERN" in str(ne_instruments.intro) or not ne_instruments.intro or "?" in str(ne_instruments.intro):
                    ne_instruments.intro = "<p>हामी CERN खुला हार्डवेयर अनुमतिपत्र (Open Hardware Licence) अन्तर्गत आफ्नै वैज्ञानिक उपकरणहरू निर्माण गर्छौं। यसले हाम्रो अनुसन्धान पूर्ण रूपमा पुनरुत्पादन योग्य र किफायती छ भन्ने कुरा सुनिश्चित गर्दछ।</p>"
                    modified = True
                if modified:
                    ne_instruments.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali InstrumentIndexPage translation!"))

            ne_data = DataPage.objects.filter(locale=ne_locale).first()
            if ne_data:
                modified = False
                if ne_data.title == "Open Data" or ne_data.title == "Live Data" or not ne_data.title or "?" in str(ne_data.title):
                    ne_data.title = "खुला तथ्याङ्क"
                    modified = True
                if "Explore real-time" in str(ne_data.intro) or "वास्तविक समय" in str(ne_data.intro) or not ne_data.intro or "?" in str(ne_data.intro):
                    ne_data.intro = "<p>नेपालमा स्थापित हाम्रा मापन केन्द्रहरूबाट प्राप्त वास्तविक समय (real-time) को तथ्याङ्क र ऐतिहासिक अभिलेखहरू अन्वेषण गर्नुहोस्।</p>"
                    modified = True
                if "access real-time" in str(ne_data.api_docs) or "JSON" in str(ne_data.api_docs) or not ne_data.api_docs or "?" in str(ne_data.api_docs):
                    ne_data.api_docs = "<p>तपाईं वास्तविक समयको JSON तथ्याङ्क <code>/api/data/latest/</code> मा पहुँच गर्न सक्नुहुन्छ र CSV फाइलहरू <code>/api/data/download/</code> बाट डाउनलोड गर्न सक्नुहुन्छ।</p>"
                    modified = True
                if modified:
                    ne_data.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali DataPage translation!"))

            ne_education = EducationIndexPage.objects.filter(locale=ne_locale).first()
            if ne_education:
                modified = False
                if ne_education.title == "Education" or ne_education.title == "Education Programmes" or not ne_education.title or "?" in str(ne_education.title):
                    ne_education.title = "शैक्षिक कार्यक्रमहरू"
                    modified = True
                if "education programmes bring" in str(ne_education.intro) or "HICS का शैक्षिक" in str(ne_education.intro) or not ne_education.intro or "?" in str(ne_education.intro):
                    ne_education.intro = "<p>HICS का शैक्षिक कार्यक्रमहरूले वैज्ञानिक उपकरण, तथ्याङ्क, र वास्तविक वैज्ञानिक अभ्यासलाई सीधै विद्यालय र समुदायहरूमा पुर्‍याउँछन्। यो पाठ्यपुस्तकमा मात्र सीमित विज्ञान होइन — विद्यार्थीहरूले आफ्नो वरपरको संसारबाट वास्तविक सङ्केतहरू सङ्कलन गर्ने उपकरणहरूबाट प्राप्त तथ्याङ्कहरूको प्रत्यक्ष विश्लेषण गर्छन्।</p>"
                    modified = True
                if modified:
                    ne_education.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali EducationIndexPage translation!"))

            ne_notes = LabNoteIndexPage.objects.filter(locale=ne_locale).first()
            if ne_notes:
                modified = False
                if ne_notes.title == "Lab Notes" or not ne_notes.title or "?" in str(ne_notes.title):
                    ne_notes.title = "प्रयोगशाला टिपोटहरू"
                    modified = True
                if "Dispatches from the field" in str(ne_notes.intro) or "स्थलगत अनुभव" in str(ne_notes.intro) or not ne_notes.intro or "?" in str(ne_notes.intro):
                    ne_notes.intro = "<p>हाम्रा वैज्ञानिक तथा अनुसन्धानकर्ताहरूका नवीनतम स्थलगत अनुभवहरू, प्राविधिक टिपोटहरू र प्रयोगशालाका नियमित गतिविधिहरू यहाँ पढ्नुहोस्।</p>"
                    modified = True
                if modified:
                    ne_notes.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali LabNoteIndexPage translation!"))

            # 6. Populate default translations for Research Programmes in Nepali locale
            ne_prog = ResearchProgrammePage.objects.filter(locale=ne_locale, slug="atmospheric-science").first()
            if ne_prog:
                modified = False
                if ne_prog.title == "Atmospheric Science" or not ne_prog.title or "?" in str(ne_prog.title):
                    ne_prog.title = "वायुमण्डलीय विज्ञान"
                    modified = True
                if "Monitoring atmospheric parameters" in str(ne_prog.summary) or not ne_prog.summary or "?" in str(ne_prog.summary):
                    ne_prog.summary = "काठमाडौं उपत्यकाको वायुमण्डलीय सूचकहरू, सूक्ष्म कण (PM2.5), र हरितगृह ग्यासहरूको निरन्तर मापन तथा विश्लेषण।"
                    modified = True
                if modified:
                    ne_prog.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Atmospheric Science translation!"))

            # 7. Populate default translations for Instruments in Nepali locale
            ne_inst = InstrumentPage.objects.filter(locale=ne_locale, slug="iesh-v0").first()
            if ne_inst:
                modified = False
                if ne_inst.title == "IESH v0 Station" or not ne_inst.title or "?" in str(ne_inst.title):
                    ne_inst.title = "IESH v0 मापन केन्द्र"
                    modified = True
                if "first integrated environmental sensing" in str(ne_inst.summary) or not ne_inst.summary or "?" in str(ne_inst.summary):
                    ne_inst.summary = "हाम्रो पहिलो एकीकृत वातावरणीय मापन प्रणाली, जसलाई उच्च-विश्वसनीय वायु र मौसम सम्बन्धी तथ्याङ्क सङ्कलनका लागि डिजाइन गरिएको हो।"
                    modified = True
                if "Measures Temperature" in str(ne_inst.what_it_measures) or not ne_inst.what_it_measures or "?" in str(ne_inst.what_it_measures):
                    ne_inst.what_it_measures = "<p>तापक्रम, आर्द्रता, वायुमण्डलीय चाप, सूक्ष्म धूलोका कणहरू (PM1.0, PM2.5, PM10), र कार्बनडाइअक्साइड (CO2) मापन गर्दछ।</p>"
                    modified = True
                if modified:
                    ne_inst.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali IESH v0 Instrument translation!"))

            # 8. Populate default translations for Education Programmes in Nepali locale
            ne_residency = EducationProgrammePage.objects.filter(locale=ne_locale, slug="residency").first()
            if ne_residency:
                modified = False
                if ne_residency.title == "School Science Residency Programme" or not ne_residency.title or "?" in str(ne_residency.title):
                    ne_residency.title = "विद्यालय विज्ञान आवासीय कार्यक्रम"
                    modified = True
                if "Multi-day visits to schools" in str(ne_residency.summary) or not ne_residency.summary or "?" in str(ne_residency.summary):
                    ne_residency.summary = "काठमाडौं बाहिरका विद्यालयहरूमा बहु-दिवसीय भ्रमण, जस अन्तर्गत तारा-मण्डल (प्लानेटेरियम) प्रदर्शन, वैज्ञानिक उपकरण निर्माण कार्यशाला, तथ्याङ्क विश्लेषण र शिक्षक तालिम समावेश छन्।"
                    modified = True
                if "primarily outside Kathmandu" in str(ne_residency.target_audience) or not ne_residency.target_audience or "?" in str(ne_residency.target_audience):
                    ne_residency.target_audience = "काठमाडौं उपत्यका बाहिरका विद्यालयहरू"
                    modified = True
                if modified:
                    ne_residency.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Residency Programme translation!"))

            ne_fellowship = EducationProgrammePage.objects.filter(locale=ne_locale, slug="fellowship").first()
            if ne_fellowship:
                modified = False
                if ne_fellowship.title == "Youth Research Fellowship" or not ne_fellowship.title or "?" in str(ne_fellowship.title):
                    ne_fellowship.title = "युवा अनुसन्धान फेलोसिप"
                    modified = True
                if "Full-time 12" in str(ne_fellowship.summary) or not ne_fellowship.summary or "?" in str(ne_fellowship.summary):
                    ne_fellowship.summary = "नेपाली वैज्ञानिक र इन्जिनियरहरूका लागि १२ देखि २४ महिनाको पूर्ण-कालीन अनुसन्धान अवसर। वास्तविक अनुसन्धान, सम्मानजनक वृत्ति (स्टाइपेन्ड), र आधिकारिक प्रकाशनहरू।"
                    modified = True
                if "Nepali scientists and engineers" in str(ne_fellowship.target_audience) or not ne_fellowship.target_audience or "?" in str(ne_fellowship.target_audience):
                    ne_fellowship.target_audience = "नेपाली वैज्ञानिक तथा इन्जिनियरहरू"
                    modified = True
                if modified:
                    ne_fellowship.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Fellowship translation!"))

            ne_camp = EducationProgrammePage.objects.filter(locale=ne_locale, slug="camp").first()
            if ne_camp:
                modified = False
                if ne_camp.title == "Annual Science Camp" or not ne_camp.title or "?" in str(ne_camp.title):
                    ne_camp.title = "वार्षिक विज्ञान शिविर"
                    modified = True
                if "Ten-day residential programme" in str(ne_camp.summary) or not ne_camp.summary or "?" in str(ne_camp.summary):
                    ne_camp.summary = "नेपालभरिबाट छनोट भएका माध्यमिक तह (कक्षा ९–११) का विद्यार्थीहरूका लागि १० दिवसीय आवासीय कार्यक्रम। काठमाडौं उपत्यका बाहिरका विद्यार्थीहरूलाई विशेष प्राथमिकता।"
                    modified = True
                if "Grades 9-11" in str(ne_camp.target_audience) or not ne_camp.target_audience or "?" in str(ne_camp.target_audience):
                    ne_camp.target_audience = "माध्यमिक तहका विद्यार्थीहरू (कक्षा ९-११)"
                    modified = True
                if modified:
                    ne_camp.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Science Camp translation!"))

            ne_teachers = EducationProgrammePage.objects.filter(locale=ne_locale, slug="teachers").first()
            if ne_teachers:
                modified = False
                if ne_teachers.title == "Teacher Professional Development" or not ne_teachers.title or "?" in str(ne_teachers.title):
                    ne_teachers.title = "शिक्षक व्यावसायिक विकास कार्यक्रम"
                    modified = True
                if "one-week residential intensive" in str(ne_teachers.summary) or not ne_teachers.summary or "?" in str(ne_teachers.summary):
                    ne_teachers.summary = "वार्षिक एक-हप्ते आवासीय सघन तालिम। शिक्षकहरू आफैंले निर्माण गरेको कार्यशील उपकरण, पठनपाठनका लागि तयार पाठ्यक्रम मोड्युल, र निरन्तर व्यावसायिक सञ्जालको सदस्यता प्राप्त गरी फर्कन्छन्।"
                    modified = True
                if "Teachers across Nepal" in str(ne_teachers.target_audience) or not ne_teachers.target_audience or "?" in str(ne_teachers.target_audience):
                    ne_teachers.target_audience = "नेपालभरिका शिक्षकहरू"
                    modified = True
                if modified:
                    ne_teachers.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Teacher Development translation!"))

            # 9. Populate default translations for Learn & Open Knowledge in Nepali locale
            ne_learn = LearnIndexPage.objects.filter(locale=ne_locale).first()
            if ne_learn:
                modified = False
                if ne_learn.title == "Learning Resources" or not ne_learn.title or "?" in str(ne_learn.title):
                    ne_learn.title = "सिकाइ सामग्रीहरू"
                    modified = True
                if "freely available" in str(ne_learn.intro) or "HICS" in str(ne_learn.intro) or not ne_learn.intro or "?" in str(ne_learn.intro):
                    ne_learn.intro = "<p>HICS का सिकाइ सामग्रीहरू शिक्षक, विद्यार्थी, र उपकरण तथा तथ्याङ्क पछाडिको विज्ञान बुझ्न चाहने जो कोहीका लागि निःशुल्क उपलब्ध छन्। डाउनलोड गर्नुहोस्, प्रयोग गर्नुहोस्, र परिमार्जन गर्नुहोस्।</p>"
                    modified = True
                if modified:
                    ne_learn.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Learning Resources translation!"))

            ne_open = OpenKnowledgePage.objects.filter(locale=ne_locale).first()
            if ne_open:
                modified = False
                if ne_open.title == "Open Knowledge" or not ne_open.title or "?" in str(ne_open.title):
                    ne_open.title = "खुला ज्ञान र साझा स्रोत"
                    modified = True
                if "public outputs exist for the world" in str(ne_open.intro) or "HICS" in str(ne_open.intro) or not ne_open.intro or "?" in str(ne_open.intro):
                    ne_open.intro = "<p>HICS का सार्वजनिक नतिजाहरू केवल हाम्रा आफ्नै कार्यक्रमहरूका लागि मात्र नभई सम्पूर्ण विश्वका लागि हुन्। हाम्रा सबै तथ्याङ्कहरू खुला छन्, उपकरणका डिजाइनहरू खुला-स्रोत छन्, र सिकाइ सामग्रीहरू निःशुल्क उपलब्ध छन्।</p>"
                    modified = True
                if modified:
                    ne_open.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS("Populated default Nepali Open Knowledge translation!"))

        except Exception as sync_err:
            self.stdout.write(self.style.WARNING(f"Could not synchronize translated trees: {sync_err}"))

        self.stdout.write(self.style.SUCCESS("HICS Database Seeding Complete!"))

