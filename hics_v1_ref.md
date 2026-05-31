# HICS Website — Version 1 Content & Page Reference

_himalayansciences.org_
_May 2026 — For coding agents and content editors_

---

## Context: What Is Real Right Now

Before writing anything, be clear about what exists and what doesn't.
Never misrepresent status. Honest placeholders beat false confidence.

**Active and producing data:**

- IESH v0 — home station, Kathmandu — temperature, humidity, pressure, PM2.5 proxy
- Crystal Mountain School thermal sensors — being installed during construction of multipurpose hall, Dolpo 4,000m — interior/exterior temperature differential

**In progress / being built:**

- IESH modular system — additional sensor modules (PM2.5 proper, CO₂, UV, rain, wind)
- IESH deployment beyond home station — school sites planned
- Portable inflatable planetarium — planned, not yet built

**Research / writing in progress:**

- Case study paper: _Thermal Sovereignty and Vernacular Resilience_ — practitioner-led study of passive solar construction in Dho Tarap, Dolpo. 7+ years of embedded community work. In-situ thermal data. Under preparation.

**In progress — not yet producing data but actively being developed:**

- Cosmic ray muon detector — instrument in development; gets its own stub page

**Planned — mention briefly, no full pages in v1:**

- Meteor camera
- SDR radio station
- Seismometer network
- Weather balloon
- Portable planetarium — gets a full instrument page (fundable, compelling vision)

---

## Tech Stack (Already Implemented)

- **Framework:** Django 5.x + Wagtail 6.x
- **Database:** MySQL (cPanel)
- **Hosting:** NestNepal cPanel, Passenger/WSGI
- **Python:** 3.11 (cPanel) / 3.12 (local dev)
- **CI/CD:** GitHub Actions → SSH deploy
- **Static files:** WhiteNoise
- **Frontend:** Django templates, Alpine.js (minimal), Chart.js for data, Leaflet.js for maps

---

## Design Language (Already Implemented)

**Typography:**

- Headings / display: `IBM Plex Mono` — monospace, signals instruments and measurement
- Body: `Source Serif 4` — warm, readable
- Data/numbers: monospace, `font-variant-numeric: tabular-nums`

**Colours:**

```
--bg:         #0d0f14
--surface:    #141720
--border:     #1e2235
--text:       #e2e4ed
--text-muted: #6b7394
--accent:     #4a9eff
--amber:      #f0a030
--green:      #3ddc84
--red:        #ff5555
```

**Tone:** Direct, evidence-forward, written as a working scientist.
No NGO-speak. No grant-proposal voice. Show the work.

**Signature header element:**

```
▸ KTM-001  22.4°C  68% RH  856 hPa  ● live
```

Persistent, monospace, real. Updates from `/api/data/latest/`.

---

## Logo — Usage Rules

**The logo file:** `hics/static/img/hics-wordmark.svg`
Source: `default_filldot.svg` (uploaded). Do not modify the source SVG.
Copy to static directory and reference via `{% static %}`.

**What the logo contains:**

- Mountain profile polygon — colour `#6296cf` (close to `--accent`)
- Amber dashed line — the muon/particle track — colour `#f0a031` (matches `--amber`)
- Amber filled circle at line end — the detector hit
- **HICS** — large, `#e2e4ed`
- _Himalayan Institute for Contextual Sciences_ — medium, `#6c7394`
- Tagline line — small, `#6c7394`

The mark (mountain + track + circle) is the symbol.
The text is the wordmark. Together they are the logo.

**The amber track is the key idea:** a particle trajectory from
upper-left (incoming cosmic ray) crossing the mountain profile
and terminating at the detector dot. This is muography —
the same physics as the PRD paper — made into a mark.

---

### Logo in the Navbar

The full wordmark (493×110px) is too wide for the navbar.
Use **mark + "HICS" text only**. Approx 140px wide, 36px tall.

```html
<!-- In base.html -->
<a
  href="/"
  class="site-logo"
  aria-label="HICS — Himalayan Institute for Contextual Sciences"
>
  <svg viewBox="0 0 200 115" height="36" aria-hidden="true">
    <!-- Mountain polygon — left portion of the full SVG -->
    <polygon
      fill="#6296cf"
      points="13.97 110.03 9.42 110.03 61.05 14.75 84.3 50.11
              111.4 0 161.4 110.03 156.97 110.03 111.08 8.99
              84.63 57.9 61.38 22.53 13.97 110.03"
    />
    <!-- Amber track — simplified for small size -->
    <line
      x1="0"
      y1="43"
      x2="185"
      y2="103"
      stroke="#f0a031"
      stroke-width="4"
      stroke-dasharray="8 5"
      stroke-linecap="round"
    />
    <!-- Detector hit -->
    <circle fill="#f0a031" cx="186" cy="101" r="9" />
  </svg>
  <span class="site-logo__text">HICS</span>
</a>
```

```css
.site-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
}
.site-logo__text {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.02em;
}
.site-logo:hover {
  text-decoration: none;
}
.site-logo:hover .site-logo__text {
  color: var(--accent);
}
```

---

### Logo in the Footer

Use the **full wordmark SVG** at reduced scale.
The footer has space; this is where the full institutional identity sits.

```html
<!-- In base.html footer -->
<div class="site-footer__brand">
  <img
    src="{% static 'img/hics-wordmark.svg' %}"
    alt="Himalayan Institute for Contextual Sciences"
    height="55"
    class="site-footer__logo"
  />
  <div class="site-footer__coords text-mono">
    Kathmandu, Nepal · 27.7172°N 85.3240°E
  </div>
  <div class="site-footer__reg">
    Himalayan Institute For Contextual Sciences Pvt. Ltd. · Registered Nepal
    Companies Act 2063
  </div>
</div>
```

```css
.site-footer__logo {
  display: block;
  /* SVG is dark-background-native — renders fine on --bg */
  margin-bottom: var(--s3);
  opacity: 0.9;
}
.site-footer__coords {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: var(--s2);
}
.site-footer__reg {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: var(--s1);
}
```

---

### Favicon

Use just the mark portion — mountain + track + circle — no text.
Crop viewBox to `0 0 200 115`, add background rect `#0d0f14`.

```html
<!-- In <head> of base.html -->
<link rel="icon" href="{% static 'img/hics-mark.svg' %}" type="image/svg+xml" />
```

Create `hics-mark.svg` as a separate file:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 115">
  <rect width="200" height="115" fill="#0d0f14"/>
  <polygon fill="#6296cf"
    points="13.97 110.03 9.42 110.03 61.05 14.75 84.3 50.11
            111.4 0 161.4 110.03 156.97 110.03 111.08 8.99
            84.63 57.9 61.38 22.53 13.97 110.03"/>
  <line x1="0" y1="43" x2="185" y2="103"
        stroke="#f0a031" stroke-width="5"
        stroke-dasharray="10 6" stroke-linecap="round"/>
  <circle fill="#f0a031" cx="186" cy="101" r="10"/>
</svg>
```

---

### Static file locations

```
hics/static/img/
  ├── hics-wordmark.svg    ← full logo (copy of default_filldot.svg)
  └── hics-mark.svg        ← mark only, with dark bg rect (for favicon)
```

---

### On light backgrounds

The SVG is designed for dark backgrounds. If ever used on a light
background (e.g. print, partner documents), the text colours
`#e2e4ed` and `#6c7394` will not read. Create a light variant
with `#0d0f14` text and `#3a5a8a` mountain — but this is not
needed for the website itself.

---

## Site Structure — Version 1

```
himalayansciences.org/
│
├── /                               Home
├── /about/                         About HICS + founder bio
├── /research/                      Research index
│   ├── /research/atmospheric/      Atmospheric science (active)
│   ├── /research/building-physics/ Building physics + CMS paper (active)
│   ├── /research/cosmic-ray/       Cosmic ray / muon physics (in progress)
│   └── /research/seismology/       Seismology (planned stub)
├── /instruments/                   Instruments index
│   ├── /instruments/iesh/          IESH hub — primary instrument page
│   ├── /instruments/muon-detector/ Muon detector (in progress stub)
│   ├── /instruments/planetarium/   Portable planetarium (planned)
│   └── /instruments/               Other planned instruments listed on index
├── /data/                          Live data dashboard + downloads
├── /education/                     Education programmes index  ← NEW
│   ├── /education/residency/       School Science Residency Programme
│   ├── /education/fellowship/      Youth Research Fellowship
│   ├── /education/camp/            Annual Science Camp
│   └── /education/teachers/        Teacher Professional Development
├── /notes/                         Lab notes index
│   └── /notes/<slug>/
├── /learn/                         Open learning resources (free, public)
│   ├── /learn/curriculum/          Downloadable curriculum modules
│   ├── /learn/build-guides/        Instrument build guides
│   └── /learn/computing/           Scientific computing tutorials
├── /open-knowledge/                Open Knowledge overview  ← NEW
│   ├── (links to /data/ for dashboards and API)
│   └── (links to /learn/ for open curricula)
└── /contact/                       Contact

Note on Education vs Learn distinction:
- /education/ — HICS's structured programmes (residency, fellowship, camp,
  teacher training). These involve applying, enrolling, or booking.
- /learn/ — freely available public resources (PDFs, guides, notebooks).
  No application needed. Download and use.
```

---

## Page 1 — Home (`/`)

The homepage tells the story in one scroll. Each section answers
a different question a first-time visitor has.

### Section 1 — Hero

**Purpose:** What is this? Answer in under 10 seconds.

```
HIMALAYAN INSTITUTE FOR
CONTEXTUAL SCIENCES
```

Tagline beneath, Source Serif 4, medium:

> Science rooted in place. Data open to all.

One short paragraph:

> An independent research, instrumentation, and learning institution
> in Kathmandu, Nepal. We build instruments, collect data, and do science
> that is about here — the atmosphere above these mountains, the ground
> beneath these cities, the communities living at altitude.

Two inline text links: `→ About HICS` · `→ Our instruments`

**No stock photography. No decorative image.**
If a photo is used anywhere near the hero, it must be a real photo:
IESH station hardware, Dolpo landscape, CMS construction site.

---

### Section 2 — Live Data Widget

**Purpose:** Is this real? Yes — here is a number from right now.

This is the single most important element on the page.
A visitor who sees real live data immediately understands
that HICS is operational, not aspirational.

```
● LIVE · KTM-001 · Kathmandu · 1,350m · [timestamp]

  22.4°      68%        856.1        47
   °C         RH         hPa       μg/m³
  TEMP    HUMIDITY    PRESSURE     PM2.5
```

Below readings: a 24-hour sparkline for temperature.
Just a line — no axes labels. The shape of the day is enough.

If Dolpo station is syncing, show a secondary strip:

```
◐ SYNC · DLP-001 · Crystal Mountain School, Dolpo · 4,000m
  Interior 14.2°C · Exterior −3.1°C · ΔT 17.3°C
```

This juxtaposition — city station and 4,000m station side by side —
communicates the altitude gradient research without explaining it.

Link: `→ Full data dashboard and downloads`

**Placeholder state** (if data is not yet flowing):
Show the widget frame. Border dashed. Values as `—`.
Label: `Station KTM-001 — coming online`. Never hide the widget.

**Implementation:** JS fetch from `/api/data/latest/?station=KTM-001`
on page load. Auto-refresh every 60 seconds.

---

### Section 3 — Station Map

**Purpose:** Where is this work happening? Show it.

Leaflet.js map, CARTO dark tiles, full-width.
Nepal centered, zoom ~7 to show the whole country.

**Markers to show:**

Active stations — green pulsing dot:

- `KTM-001` · 27.6915°N 85.3205°E · Kathmandu · IESH Environmental
- `DLP-001` · 29.0469°N 82.9481°E · Dolpo · CMS Thermal Monitor

Planned stations — grey outlined dot:

- `KTM-002` · Kathmandu · IESH school deployment
- `PKR-001` · Pokhara · IESH school deployment (planned)
- `DHR-001` · Dharan · IESH school deployment (planned)
- `BTW-001` · Bharatpur · IESH school deployment (planned)

Each marker: click → popup with station name, type, status,
and latest reading if live.

**Below map, one line:**

```
2 stations active · 4 school deployments planned · open data from day one
```

**Implementation note:** markers loaded from `/api/stations/` JSON
endpoint — add this API route. Falls back to hardcoded JS array
if API is unavailable.

---

### Section 4 — Active Programmes

**Purpose:** What is actually happening right now?

Section label: `ACTIVE WORK`

Two active cards + one in-progress card:

**Card 1 — IESH Environmental Monitor**
Status: `● Active`
Photo: IESH home station hardware (use real photo)

> Continuous atmospheric monitoring from Kathmandu.
> Temperature, humidity, pressure, air quality. Data syncing live
> to himalayansciences.org. First in a network of stations
> planned across Nepal's altitude gradient.
> Link: `→ Instrument details and live data`

**Card 2 — Crystal Mountain School, Dolpo**
Status: `● Active`
Photo: CMS building or Dolpo landscape (use real photo)

> Thermal performance monitoring during construction of a passive
> solar multipurpose hall at 4,000m in Dho Tarap. Sensor installation
> underway as the hall is built. Interior and exterior temperature
> tracked continuously — the first empirical thermal dataset for
> passive solar construction at this altitude in Nepal.
> Link: `→ Building physics programme`

**Card 3 — Cosmic Ray Muon Detector**
Status: `◎ In progress`

> Open-source cosmic ray muon detector for the Himalayan altitude-flux
> network. Based on plastic scintillator and silicon photomultiplier.
> In development — the instrument that will generate the first
> systematic muon dataset across Nepal's altitude gradient.
> Link: `→ Muon detector`

---

### Section 5 — The Scientific Context (Data Gap)

**Purpose:** Why does this matter? Show the gap, not just the work.

Section label: `THE GAP IN THE DATA`

Brief intro text:

> Nepal sits at the intersection of some of the most important
> scientific questions of our time — atmospheric pollution,
> seismic hazard, climate adaptation, cosmic ray physics.
> It is also one of the most under-instrumented countries on Earth.
> HICS is building the measurement infrastructure to change this.

Three panels, rendered as simple SVG illustrations or static charts:

**Panel A — Atmospheric monitoring**
South Asia outline. Dense sensor dots in India.
Nepal: sparse. High-altitude zones: empty.
Caption: _Nepal's high-altitude atmosphere is almost entirely
unmeasured. Transboundary pollution from the Indo-Gangetic Plain
reaches the Himalaya — there is almost no data on what arrives,
or how it changes with altitude._

**Panel B — Cosmic ray flux (future programme)**
Altitude vs. muon flux schematic. Theoretical curve shown.
Existing data points plotted at sea level and European mountain
stations. A shaded band over 1,000–5,000m marked:
`No systematic measurements — Himalayan region`.
Caption: _Nepal's altitude gradient — from 60m to 8,848m —
is the most dramatic on Earth. It has never been systematically
measured for cosmic ray muon flux. HICS's muon detector programme
will generate this dataset._

**Panel C — Building performance data (active programme)**
Schematic of a building cross-section. Temperature probe positions.
Interior vs exterior temperature curves.
Caption: _Passive solar design for Himalayan conditions requires
local empirical data. None exists at high altitude in Nepal.
The Crystal Mountain School dataset is the first._

**Implementation:** These three panels are static SVG — not
interactive charts. Design them once, update text as needed.
Keep them clean: dark background, accent blue lines, muted labels.

---

### Section 6 — Instruments in Development

**Purpose:** What's being built next? Show the roadmap.

Section label: `IN THE PIPELINE`

Compact list — one line each with accurate status:

```
◎  IESH v1 — modular hub      PM2.5, CO₂, UV, rain, wind add-on modules
◎  IESH school deployment      First school stations outside Kathmandu
◎  Cosmic ray muon detector    In development — altitude-flux network
○  Portable planetarium        Inflatable dome, Nepali-language programmes
○  All-sky meteor camera       Nepal's first GMN contribution
○  MEMS seismometer            Kathmandu Valley earthquake network
○  SDR radio station           Meteor scatter, lightning, ionosphere
○  Weather balloon             Atmospheric profiling to 30km
```

One line below:

> All instrument designs published open-source.
> Any institution anywhere can build them.

Link: `→ Full instrument list`

---

### Section 7 — Education Programmes Teaser

**Purpose:** show that HICS is more than instruments and data —
it is a learning institution with structured programmes.

Section label: `EDUCATION & LEARNING`

Brief intro (2 sentences):

> HICS's education programmes bring instruments, data, and scientific
> practice directly into schools and communities. Not textbook science —
> students analyse real data from real instruments collecting real signals.

Four compact programme cards, horizontal row:

**School Science Residency**

> Multi-day visits to schools combining planetarium sessions,
> instrument workshops, and data analysis. Schools enter lasting
> relationships, not one-off events.
> `→ Learn more`

**Youth Research Fellowship**

> Full-time 12–24 month research positions for Nepali scientists.
> Co-authored publications. A real alternative to leaving Nepal
> to do science.
> `→ Learn more`

**Annual Science Camp**

> Ten-day residential programme for high school students from
> across Nepal. Priority for students from districts outside
> Kathmandu.
> `→ Learn more`

**Teacher Development**

> Residential intensive. Teachers leave with a working instrument
> they built, curriculum modules ready to teach, and membership
> in an ongoing professional community.
> `→ Learn more`

Link below cards: `→ All education programmes` · `→ Free learning resources`

---

### Section 7 — Latest from the Lab

**Purpose:** Show that things are actually happening, regularly.

Three most recent lab notes, auto-populated from Wagtail.
Each: date · type tag · title · 2-sentence summary · link.

At launch, these three notes must exist:

1. IESH v0 build log
2. Crystal Mountain School — sensor installation dispatch
3. One more: either the CMS paper announcement or an
   atmospheric data first-look

---

### Section 8 — Footer CTA

Four paths, one line each:

```
Researcher?   We are looking for collaborators in atmospheric
              science, earth science, and physics. → Write to us

Student?      Research fellowships for Nepali scientists who
              want to do science here, not abroad. → Learn more

Teacher?      Instruments, data, and programmes for schools
              across Nepal. → School partnerships

Funder?       We are building something that does not exist
              anywhere else in this region. → What we're building
```

---

## Page 2 — About (`/about/`)

**Purpose:** Establish credibility. Make HICS real as an institution.
Give a serious visitor — professor, funder, collaborator — everything
they need to decide to engage.

### Section 1 — Who We Are

> Himalayan Institute for Contextual Sciences (HICS) is an independent
> research, instrumentation, and learning institution based in
> Kathmandu, Nepal.

> We are built on a single organising principle: that Nepal's geography,
> ecology, seismology, atmosphere, and cultural knowledge are not
> obstacles to doing serious science — they are the material.
> Science done here should be about here.

> HICS works across four domains — Research, Instrumentation, Education,
> and Open Knowledge — without artificially separating them. The same
> instruments, data, and scientific questions serve researchers, students,
> teachers, and communities simultaneously.

---

### Section 2 — The Problem

Header: `THE PROBLEM WE ARE ADDRESSING`

> Nepal faces a structural translational gap — a broken chain between
> scientific knowledge and the people, places, and questions that
> most need it.

> Research institutions operate in isolation from students and communities.
> Schools operate without research infrastructure. Talented graduates leave
> because meaningful scientific careers require going abroad. Research about
> Nepal is routinely conducted by outsiders. Communities facing climate
> change, earthquakes, and pollution lack access to local scientific data
> about the phenomena directly affecting them.

> HICS addresses this not by improving each broken link separately,
> but by building a different structure entirely.

Display as a visual flow element — monospace, horizontal with arrows:

```
Instruments → Data → Questions → Methods → Results → Publications → Identity → More Instruments
```

> This chain is not linear. Any point is an entry point. A student
> can enter through a question or a dataset. A researcher enters through
> an instrument or an open data platform. A community member enters
> through a public dashboard showing their neighbourhood's air quality.
> The depth of engagement is not predetermined — the same sensor node
> is a science education tool for a Grade 8 student and a research
> instrument for an atmospheric scientist.

> The identity shift is the theory of change. When a student in Jumla
> collects data that is downloaded by researchers in Switzerland,
> something changes in how they understand what they are.

---

### Section 3 — Vision

Header: `OUR VISION`

> A Nepal where serious science happens here — rooted in this geography,
> conducted by people from this place, generating knowledge that returns
> to the communities that need it.

Five vision statements — displayed as a list with subtle left border rule:

- HICS is Nepal's most credible independent research institute for
  physics, atmospheric science, earth science, and science education —
  publishing internationally, contributing to global datasets.
- Instruments designed and built by HICS are deployed across hundreds
  of schools in Nepal and replicated by institutions in other countries —
  making contextual, open-source scientific hardware a Nepali export.
- Nepali researchers who might have left to do science abroad have
  chosen instead to stay, build, and publish here.
- HICS's open data — air quality, seismic activity, atmospheric profiles —
  is freely used by government agencies, researchers, farmers, and students.
- The model HICS demonstrates — contextual, open, integrated research
  and learning — has been adopted and adapted by similar institutions
  in the Andes, East Africa, and Central Asia.

---

### Section 4 — Mission

Large display text, IBM Plex Mono, centred or left-aligned:

> To advance science and scientific learning through research, open
> instrumentation, and education deeply rooted in Nepal's geographic,
> ecological, and cultural realities — building the translational
> infrastructure that makes doing serious science in Nepal possible.

---

### Section 5 — How We Work

Six principles. Bold label + 2 sentences each. No bullets.

**Contextual.** Science done here is about here. Nepal's altitude
gradient, seismology, atmosphere, communities, and traditional knowledge
are not constraints on imported research agendas — they are the subject.

**Open.** All data published openly. All instrument designs open-source.
All learning materials freely available. Openness is the fastest path
to credibility, collaboration, and impact.

**Integrated.** Research and education are not separate departments.
The same instruments and datasets serve a researcher, a teacher,
and a student in the same afternoon.

**Rigorous.** Accessibility does not mean compromised standards.
Peer-reviewed methodology and honest uncertainty quantification are
non-negotiable at every level of HICS's work.

**Embedded.** HICS does not deliver programmes and leave. It builds
instruments that keep generating data, relationships that outlast
funding cycles, fellows who return, datasets that grow.

**Patient.** Good institutions take time. HICS measures success
in decades, not quarters.

---

### Section 6 — Areas of Work

Four domains, each with a 2-sentence summary and link:

**Research** — Original science, openly published.
Fundamental and applied research in the physical and earth sciences,
producing peer-reviewed publications, novel datasets, and contributions
to global networks. Current focus: atmospheric monitoring and
building physics. → Research programmes

**Instrumentation** — Open-source hardware built for Nepal.
Design, fabrication, and open-source publication of affordable
scientific instruments optimised for Nepal's conditions: extreme
altitude, monsoon humidity, temperature cycling, limited connectivity.
All designs freely available for replication anywhere. → Instruments

**Education** — Instrument-based learning, Grade 5 to graduate.
Curriculum-aligned, instrument-based science education serving
students, teachers, and communities. Not textbook science — students
analyse real data from real instruments collecting real signals.
Gender equity is structural, not symbolic: fellowship selection,
camp admissions, teacher recruitment, and mentoring structures all
explicitly work to reduce barriers for women and girls.
→ Education programmes

**Open Knowledge** — Science for everyone, not only enrolled students.
Real-time public dashboards, freely downloadable datasets, open API,
open-source instrument designs and curricula, offline-first platforms
for low-connectivity schools, and policy engagement — scientific data
presented directly to government decision-makers.
→ Data · → Free learning resources

---

### Section 7 — Founder Bio

Header: `FOUNDING TEAM`

[Photo — field setting preferred, real not studio]

**Pawan Dhakal — Founder and Director**

> Physicist, educator, and institution builder. Pawan Dhakal's work
> spans particle astrophysics, national-scale educational technology,
> passive solar architecture at 4,000m, and over seven years of
> embedded community work in Nepal's high-altitude regions.

> His research in muon physics produced a publication in Physical Review D,
> one of the world's leading peer-reviewed physics journals. His work at
> Crystal Mountain School, Dolpo — co-designing passive solar buildings
> with an indigenous mountain community — combines scientific rigour with
> direct humanitarian relevance and forms the empirical basis for ongoing
> research into climate-adaptive construction for Himalayan conditions.

> His decade of experience building educational technology infrastructure
> for Nepal informs HICS's approach to open-source instrument design:
> tools that work in Dolpo in January must be designed differently from
> tools designed for a temperate-climate university lab.

> HICS is the institution that brings these threads together.

[GitHub link] · [Contact link]

**Who joins next:**

> HICS is designed for others to join — as research partners,
> co-directors, research fellows, instrumentation engineers, and
> educators. If you are a scientist, engineer, or educator who sees
> what HICS is building and wants to be part of it, write to us.
> → Contact

---

### Section 8 — International Scientific Networks

Header: `INTERNATIONAL SCIENTIFIC NETWORKS`

> HICS participates in and contributes data to established global
> networks, making Nepal's scientific output legible to the
> international community from day one.

Displayed as horizontal tags — active first, future marked:
`OpenAQ` · `PANGAEA` · `Global Meteor Network ↗` · `Raspberry Shake Network ↗` · `Blitzortung Lightning Network ↗` · `FDSN ↗`

(↗ = future contribution when instrument is deployed)

> Every contribution to these networks means a researcher anywhere
> downloading Nepal's data and citing it — extending HICS's scientific
> reach with zero marginal cost.

---

### Section 9 — Research Programmes Full List

This section ensures the About page communicates the full breadth
of the HICS research vision, even where programmes are planned.

Header: `RESEARCH PROGRAMMES`

List all programmes with one-line descriptions:

**Active:**

- Atmospheric science — air quality networks, meteorological monitoring across altitude gradient
- Building physics — thermal monitoring and passive solar design for Himalayan conditions

**In progress:**

- Cosmic ray physics — systematic measurement of muon flux across Nepal's altitude gradient

**Planned:**

- Meteor astronomy — Nepal's contribution to the Global Meteor Network
- Seismology — dense sensor networks across Kathmandu Valley
- Traditional ecological knowledge — indigenous astronomical and environmental knowledge documentation, communities as co-owners of results
- Glaciology and cryosphere — field monitoring of Himalayan glaciers, water security
- Computational science — machine learning for environmental time-series analysis, published openly

Link: `→ All research programmes`

---

### Section 10 — Registration

> Himalayan Institute for Contextual Sciences (HICS) is registered
> in Nepal as Himalayan Institute For Contextual Sciences Pvt. Ltd.
> under the Companies Act 2063 (2006), with registered office in
> Lalitpur, Bagmati Province.

Contact: info@himalayansciences.org

---

## Page 3 — Research Index (`/research/`)

Brief intro + programme cards with status.

Intro:

> HICS pursues original scientific research in the physical and earth
> sciences. All research is published openly. All data is freely
> downloadable. Nepal's geography makes it one of the most scientifically
> interesting places on Earth — and one of the most under-measured.

Status key:

- `● Active` — data currently being collected
- `◎ Building` — instrument under construction
- `○ Planned` — programme designed, not yet instrumented

**Programme cards for v1:**

| Programme           | Status        | Summary                                                                                      |
| ------------------- | ------------- | -------------------------------------------------------------------------------------------- |
| Atmospheric Science | ● Active      | Air quality and meteorological monitoring from Kathmandu and Dolpo                           |
| Building Physics    | ● Active      | Thermal monitoring at Crystal Mountain School; passive solar for Himalayan conditions        |
| Cosmic Ray Physics  | ◎ In progress | Altitude-flux muon network — detector in development; PRD paper is the scientific foundation |
| Seismology          | ○ Planned     | Dense MEMS seismometer network for the Kathmandu Valley                                      |

**Publications section** — on this page:

**Pawan Dhakal et al.**
_[Full PRD paper title]_
Physical Review D · [year, volume, page]
DOI: [link]

Brief plain-language summary (2–3 sentences — not the journal abstract):

> [Explain what was measured, what was found, why it matters.
> > Written for a non-specialist intelligent reader.]

Tags: `muon physics` `dark matter` `particle astrophysics`

[DOI link] · [arXiv link if available] · [Download PDF]

Note: _Published under Pawan Dhakal's prior affiliation.
This represents the scientific foundation of HICS's cosmic ray programme._

---

## Page 4 — Atmospheric Science (`/research/atmospheric/`)

Status: `● Active`
Summary: _Air quality, temperature, pressure, and humidity monitoring
across Nepal's altitude gradient._

### What we're measuring and why

> The atmosphere above Nepal is scientifically extraordinary and poorly
> documented. Kathmandu Valley's air quality is among the worst in South
> Asia — and the source attribution is poorly understood. The Himalaya
> exerts enormous influence on monsoon dynamics and transboundary aerosol
> transport. HICS is building the measurement infrastructure to study
> this systematically, from the valley floor to 4,000m and beyond.

### Current instruments

- **IESH v0, KTM-001** — Kathmandu, 1,350m — [→ Instrument page]
  Temperature · Humidity · Pressure · PM2.5 proxy · Logging since [date]

- **Environmental sensors, DLP-001** — Crystal Mountain School, Dolpo, 4,000m
  Temperature (interior + exterior) · Under installation [date]

### What we measure

PM2.5 particulate · PM10 particulate · Temperature · Relative humidity ·
Atmospheric pressure · Derived altitude · CO₂ (classroom modules) ·
UV index (v1 module) · Rainfall (v1 module) · Wind speed and direction (v1 module)

[→ Live data dashboard]

### Research questions

- What is the diurnal and seasonal pattern of PM2.5 in the Kathmandu Valley?
- How does particulate matter at 4,000m in Dolpo compare to valley
  background levels — and what fraction is locally generated
  vs. transboundary transport from the Indo-Gangetic Plain?
- How does the monsoon transition affect pollutant concentrations
  across the altitude gradient?
- What is the relationship between Kathmandu's brick kiln season
  and black carbon deposition on Himalayan glaciers?

### Future programme

- High-altitude background stations (Mustang, Solukhumbu)
- Weather balloon atmospheric profiling — temperature, humidity,
  pressure from surface to 30km
- IESH network expansion to 20+ schools across Nepal

### Data

[Download current dataset — CSV] · [API documentation]

Licence: CC BY 4.0
Citation: _HICS Atmospheric Network, [station ID], [date range].
himalayansciences.org/data_

---

## Page 5 — Building Physics (`/research/building-physics/`)

Status: `● Active`
Summary: _Thermal performance monitoring of passive solar buildings
at high altitude; climate-adaptive construction for Himalayan communities._

### The research

> Nepal's mountain communities live in some of the coldest inhabited
> environments on Earth, with buildings designed and built under
> state mandates that systematically promote urban-centric concrete
> construction that fails catastrophically in freezing winters.
> Meanwhile, traditional vernacular architecture — developed over
> centuries of lived experience with Himalayan conditions — is
> being systematically delegitimised.

> HICS's building physics programme generates the empirical data
> that this conversation has always lacked: actual measured thermal
> performance of real buildings, in real Himalayan conditions,
> over real time.

### The Crystal Mountain School Project — Dho Tarap, Dolpo (4,000m)

> The Dho Tarap valley in Dolpo is one of the most climatically
> extreme inhabited places in Nepal — cold, high, and increasingly
> squeezed between climate change and state infrastructure policy
> that actively harms community resilience.

> In 2026, Crystal Mountain School began construction of a new
> multipurpose hall designed using passive solar principles developed
> through 15+ years of community-embedded practice by Vision Dolpo.
> HICS is conducting real-time thermal monitoring throughout construction
> and into operation.

**What we're monitoring:**

- Interior surface temperatures (multiple positions)
- Exterior ambient temperature
- Solar irradiance (pyranometer)
- Relative humidity (interior and exterior)
- Construction phase documentation (timestamped)

**Why construction-phase data matters:**

> Monitoring a building while it is being built captures the thermal
> mass charging behaviour — the rate at which heavy walls and floors
> absorb and release heat. This cannot be reconstructed retrospectively.
> The dataset being collected now is unique.

[→ Live data: DLP-001 station] [→ Lab note: sensor installation]

### The Research Paper

**Work in progress — 2026:**

_Thermal Sovereignty and Vernacular Resilience: Tracing Climate
Adaptation and Technology Transfer in Dolpo, Nepal_

> This practitioner-led case study documents over seven years of
> collaborative work in the Dho Tarap community, combining longitudinal
> observation with in-situ thermal performance data comparing traditional
> vernacular buildings and passive solar constructions. The paper
> introduces the concept of "thermal sovereignty" — the community's
> reclamation of vernacular, climate-responsive design as an act of
> socio-ecological resistance against centrally imposed, climatically
> inappropriate infrastructure.

Key themes:

- Socio-technical evolution of local climate adaptation from 2008 to present
- The role of community-led knowledge exchange (2018 Ladakh visit)
  in catalysing indigenous co-design practice
- Physical resilience and material circularity: the original earthquake-
  damaged solar building dismantled and its materials recycled into
  the new multipurpose hall
- Scalability of the Dho Tarap model across the broader Dolpo region
- Environmental justice framing: the built environment as a domain
  of indigenous rights

_Expanding the environmental justice framework in Nepal beyond
forest and water rights to the built environment._

Status: under preparation. Pre-print forthcoming.

### Future programme

- Thermal monitoring across 10+ buildings at different altitude zones
  (Dolpo, mid-hills, Kathmandu, Terai)
- Passive solar vs. vernacular vs. modern concrete: empirical comparison
- Open-source design manual for passive solar buildings in Himalayan
  climate zones — quantitative guidelines based on measured data
- Policy engagement: National Building Code mountain zone provisions

---

## Page 6 — Instruments Index (`/instruments/`)

Intro:

> The instruments HICS builds are the instruments HICS uses.
> There is no separation between research tools and education tools —
> the same hardware serves a researcher, a teacher, and a student.
> All designs, firmware, and assembly documentation are published
> under open-source licences.

**Instrument status table — v1:**

| Instrument                 | Status        | Measures                              | Deployments            |
| -------------------------- | ------------- | ------------------------------------- | ---------------------- |
| IESH Environmental Monitor | ● Active      | Temp, humidity, pressure, air quality | KTM-001 · DLP-001      |
| IESH — PM2.5 module        | ◎ Building    | Particulate matter PM2.5/PM10         | Planned for KTM-001    |
| IESH — CO₂ module          | ◎ Building    | Carbon dioxide (NDIR)                 | Planned                |
| IESH — Weather module      | ○ Planned     | UV, rain, wind                        | Planned                |
| Cosmic Ray Muon Detector   | ◎ In progress | Muon flux vs. altitude                | Multiple sites planned |
| Portable Planetarium       | ○ Planned     | Mobile astronomy education            | Mobile                 |
| All-Sky Meteor Camera      | ○ Planned     | Meteors, fireballs                    | Kathmandu, Nagarkot    |
| MEMS Seismometer           | ○ Planned     | Ground motion                         | Kathmandu Valley       |
| SDR Radio Station          | ○ Planned     | Meteor scatter, lightning, ionosphere | Kathmandu              |

---

## Page 7 — IESH Instrument Page (`/instruments/iesh/`)

# Integrated Environmental Science Hub (IESH)

Status: `● Active` · First station: KTM-001, Kathmandu, 1,350m

### What it is

> The IESH is HICS's core monitoring platform — a modular hardware
> and software system that continuously measures the local environment,
> stores data offline-first, syncs to the HICS network when connected,
> and makes all data publicly available for download.

> The IESH is designed for Nepal's conditions: monsoon humidity,
> temperature extremes from −20°C to +40°C, intermittent power,
> and limited or absent internet connectivity. It runs offline-first —
> data is never lost because the internet is down.

> The modular design means any school or research site can start with
> the base unit and add sensors as funding and need allow. The same
> hardware platform serves a school science classroom and a high-altitude
> research station.

### Current specification — v0 (active)

**Base sensors:**

- Temperature: DHT22 + BMP280 (dual sensor, cross-validated)
- Relative humidity: DHT22
- Atmospheric pressure: BMP280
- PM2.5 air quality: MQ-135 proxy (qualitative)

**Computing:**

- Raspberry Pi 3B
- Local SQLite logging
- Auto-sync to himalayansciences.org every 10 minutes
- Flask dashboard accessible on local WiFi

### Planned modules — v1

**PM module** — PMS5003 Plantower sensor
True PM2.5 and PM10 measurement. Laser particle counter.
Replaces MQ-135 proxy with calibrated, quantitative data.

**CO₂ module** — SCD40 NDIR
Accurate CO₂ measurement for classroom air quality monitoring.
Particularly relevant for understanding ventilation in high-altitude
schools where windows must stay closed in winter.

**Weather module** — UV, rain gauge, wind speed and direction
UV index (VEML6075), tipping-bucket rain gauge,
ultrasonic anemometer (no moving parts — designed for high altitude).

**Radiation module** — SiPM-based particle detector
Cosmic ray / gamma radiation detection.
Shares data with the muon physics research programme.

**Seismic module** — ADXL355 MEMS accelerometer
Local ground motion detection. Feeds Kathmandu Valley seismic network.

### Live data

[→ Dashboard: KTM-001]
[Download full dataset — CSV]
[API: /api/data/latest/?station=KTM-001]

### Build log

[Auto-populated from lab notes tagged `iesh` and `build`]

### Design files

[→ GitHub: hics-nepal/iesh-firmware] — MIT licence
Hardware designs: CERN OHL

### Build guide

[→ Learn: IESH v0 build guide]

---

## Page 7b — Muon Detector (`/instruments/muon-detector/`)

Status: `◎ In progress`

# Cosmic Ray Muon Detector

> Cosmic rays — high-energy particles from distant supernovae and
> other astrophysical sources — continuously rain down on Earth.
> When they strike the upper atmosphere, they produce cascades of
> secondary particles including muons. Muons travel at close to the
> speed of light, penetrate deep into matter, and arrive at the
> surface in measurable numbers. That number depends on altitude,
> atmospheric pressure, and the particle physics of the cascade.

> Nepal's altitude gradient — from 60m in the Terai to over 8,000m
> in the Himalaya — is the most dramatic on Earth. No one has
> systematically measured muon flux along this gradient.
> HICS will.

### The instrument

An open-source muon detector based on plastic scintillator tiles
and silicon photomultiplier (SiPM) sensors — the same detection
principle used in large-scale particle physics experiments, scaled
to a unit that costs under NPR 25,000 to build and runs on a
Raspberry Pi.

When a muon passes through the scintillator, it produces a flash
of light. The SiPM converts this to an electrical pulse. The
Raspberry Pi timestamps it, logs it, and syncs to the HICS network.

**Key design requirements:**

- Altitude-optimised firmware with automatic atmospheric pressure correction
- GPS timing for coincidence analysis between stations
- Offline-first — logs locally, syncs when connected
- Ruggedised for −30°C to +40°C, monsoon humidity
- Bill of Materials sourced from components available in Nepal

### Why it matters

The muon flux at altitude is not simply "more cosmic rays" —
the relationship between altitude, atmospheric depth, and muon
flux encodes particle physics. The cascade decay rates are
measurable. At high altitude, muons that would decay before
reaching sea level arrive intact — a direct demonstration of
relativistic time dilation.

Measuring this systematically across Nepal's altitude gradient
generates a dataset that does not exist. It is publishable.
It is fundable. And the same instrument that does the research
teaches the physics to students at every level.

### Connection to the PRD paper

HICS's published research in Physical Review D — the search for
dark matter signals using atmospheric muon data — is the scientific
ancestor of this programme. The detection methodology, the
atmospheric physics, the signal processing: all connected.

[→ Publications]

### Current status

Instrument design complete. Component sourcing underway.
First unit in early assembly.

**Build log:** [→ Notes tagged `muon` `build`]

**Design files:** [→ GitHub: hics-nepal/instruments] — CERN OHL

### Target network

10–15 stations from Terai to high-altitude sites (Mustang, Dolpo).
First station: Kathmandu (1,350m). Second: one high-altitude site (>3,500m).
The two-station dataset — even before a full network — generates a
scientifically meaningful altitude-flux data point for Nepal.

---

Status: `○ Planned`

# Portable Inflatable Planetarium

> A mobile planetarium that fits in a vehicle and inflates in a school
> courtyard in 20 minutes. An entire school's students can experience
> an immersive sky show — without leaving their district, without
> dark skies, without clear weather.

> For most Nepali students outside Kathmandu, this is the first time
> they will have seen the full night sky. For the teacher who uses it,
> it is a teaching tool they can take to every class they ever teach.

### The system

**Hardware:**

- Inflatable dome, 5–6m diameter
- Short-throw projector
- Raspberry Pi running Stellarium / OpenSpace
- Battery-powered operation (no mains electricity required)
- Transport: fits in a standard vehicle

**Software — three original Nepali-language programmes:**

**Programme 1: The Himalayan Sky**
Traditional Nepali and indigenous astronomical knowledge — the nakshatra
system, Tibetan sky traditions, monsoon agriculture astronomy from
mountain communities — integrated with modern constellation mapping.
_The sky that our grandparents named is the same sky that physics studies._

**Programme 2: Orbits, Eclipses, and the Moving Sky**
Orbital mechanics visualised: seasons, eclipses, retrograde motion.
Historical development of astronomical understanding. How we learned
what we know.

**Programme 3: Messengers — From Meteors to Dark Matter**
The connection from visible meteors to atmospheric ionization to
particle physics — bridging the planetarium to HICS's full research
portfolio in a show designed for Grade 9–12 students.

### How it is used

The planetarium is the centrepiece of HICS's School Science Residency
Programme — a multi-day visit to a school combining:

- Planetarium shows for all students (45 min each group)
- Instrument workshop: students build and use a simple sensor
- Data exploration: students analyse real data from the IESH network
- Teacher training: teacher works alongside students, leaves with
  curriculum materials and instrument knowledge

Schools that host a residency enter a longer relationship.
The planetarium is the door; the IESH station is what stays.

### Status and timeline

Currently in design and component sourcing phase.
Target: first dome deployed in 2026.

[→ Contact us about hosting a residency]
[→ School partnerships]

---

## Page 9 — Data (`/data/`)

**This is the most important page on the site.**

### Header

```
OPEN DATA

All data produced by HICS instruments is freely available.
Download it. Use it. Cite it. Build on it.
```

### Station Status

Card row showing all active and planned stations:

| Station | Location  | Altitude | Type          | Status | Last reading |
| ------- | --------- | -------- | ------------- | ------ | ------------ |
| KTM-001 | Kathmandu | 1,350m   | Environmental | ● live | [timestamp]  |
| DLP-001 | Dolpo     | 4,000m   | Thermal       | ● live | [timestamp]  |

### Live Dashboard — KTM-001

Four reading cards: Temperature · Humidity · Pressure · PM2.5

24-hour Chart.js time series below, one chart per sensor.
Dark background. Accent blue line. No grid clutter.
Auto-refreshes every 60 seconds.

### Crystal Mountain School — DLP-001

Separate section.
Key display: interior temperature vs. exterior temperature on one chart.
Shows the thermal differential — the building doing its job.

Label: _Construction phase data — passive solar multipurpose hall,
Crystal Mountain School, Dho Tarap, Dolpo, 4,000m. Sensors installed [date]._

[→ Building physics research programme]

### Download

```
Station KTM-001 — Kathmandu Environmental Monitor
[Download full dataset — CSV]
[Download this month — CSV]

Station DLP-001 — Crystal Mountain School Thermal
[Download full dataset — CSV]
[Download this month — CSV]
```

### Open Data Commitment

> All data published by HICS is released under Creative Commons
> Attribution 4.0 (CC BY 4.0). Use it for any purpose — commercial
> or non-commercial — with attribution.

> Suggested citation:
> _Himalayan Institute for Contextual Sciences (HICS).
> [Dataset name]. [Station ID]. [Date range].
> himalayansciences.org/data_

### API Documentation

```
GET  /api/data/latest/?station=KTM-001
     → Latest reading as JSON

GET  /api/data/historical/?station=KTM-001&hours=24
     → Time series for last N hours as JSON array

GET  /api/data/download/?station=KTM-001
     → Full dataset as CSV download

POST /api/ingest/environmental/
     → Instrument data ingestion
     → Authenticated (station API key required)
     → Used by IESH units to sync data
```

### Coming Online

Placeholder sections for future data streams.
Same visual style as live sections but border dashed, values `—`.

**Cosmic Ray Flux**

> When the muon detector network is operational, this section
> will show real-time muon flux from multiple altitude stations
> across Nepal. Expected: 2027.

**Seismic Activity**

> When the Kathmandu Valley seismometer network is deployed,
> this section will show continuous ground motion data.
> Expected: 2027.

---

## Page 10 — Education Programmes (`/education/`)

**Purpose:** Show HICS as a complete learning institution, not just
a data producer. These are structured programmes — not free downloads,
but things people apply for, enrol in, or book.

Intro:

> HICS's education programmes bring instruments, data, and real
> scientific practice directly into schools and communities.
> Not textbook science — students analyse real data from real
> instruments collecting real signals from the world around them.
>
> Gender equity is structural, not symbolic. Fellowship selection,
> camp admissions, teacher recruitment, and mentoring structures
> all explicitly work to reduce barriers for women and girls.

Four programme pages, each linked from the index:

---

### `/education/residency/` — School Science Residency Programme

> Two to three day residencies in schools — primarily outside Kathmandu
> — combining portable planetarium sessions, instrument workshops,
> data exploration, and teacher training.

**What happens during a residency:**

- Planetarium shows for all students (45 min per group)
- Instrument workshop: students build and use a simple sensor
- Data session: students analyse real data from the IESH network
- Teacher training: teacher works alongside students throughout,
  leaves with curriculum materials and instrument knowledge

**Not a one-off event.** Schools that host residencies enter
a longer relationship: IESH station installation, ongoing data
access, annual follow-up visits, teacher community membership.
The residency is the door; the instrument is what stays.

Status: programme designed. First residencies planned for 2026–27
once the portable planetarium is built.

`→ Enquire about hosting a residency`
→ info@himalayansciences.org · Subject: School residency

---

### `/education/fellowship/` — Youth Research Fellowship

> Full-time 12–24 month research positions for Nepali scientists
> and engineers. Real research. Real stipend. Real publications.
> Not an internship.

**The explicit goal:** an alternative to leaving Nepal to do science.
If HICS cannot make doing science in Nepal a real and compelling
choice, something has gone wrong.

**What fellows do:**

- Co-author at least one peer-reviewed publication or contribute
  a published dataset
- Develop or improve at least one HICS instrument
- Participate in school programme delivery
- Mentor the next cohort

**Selection:** competitive, based on intellectual curiosity and
commitment to Nepal over credentials. Physics, engineering,
computing, atmospheric science, earth science, biology backgrounds
all considered.

**Stipend target:** NPR 25,000–35,000 per month — competitive
with entry-level positions in Kathmandu.

Status: programme designed. First cohort planned for 2027.
Expressions of interest welcome now.

`→ Express interest`
→ info@himalayansciences.org · Subject: Fellowship enquiry

---

### `/education/camp/` — Annual Science Camp

> Ten-day residential programme for high school students
> (Grades 9–11) selected from across Nepal. Priority for students
> from districts outside Kathmandu.

**What students do:**

- Work with HICS instruments: muon detector, IESH station,
  SDR receiver, spectroscope
- Carry out a small investigation using real instruments
- Analyse data using Python
- Present findings on the final day

**Curriculum areas:** particle physics and cosmic rays ·
atmospheric science and climate · earthquake science ·
scientific computing · traditional ecological knowledge

Students leave with access to HICS's data platform for continued
analysis. Alumni become the pipeline for research fellowships.

Target: 30–40 students per year. First camp: 2027.

`→ Register interest`
→ info@himalayansciences.org · Subject: Science camp

---

### `/education/teachers/` — Teacher Professional Development

> Annual one-week residential intensive. Teachers leave with
> a working instrument they built, curriculum modules ready to
> teach, and membership in an ongoing professional community.

**What teachers leave with:**

- A working instrument built during the week (spectroscope,
  IESH sensor node, or SDR receiver — depending on cohort)
- Three complete curriculum modules tested and adapted for their school
- Access to HICS instrument loan programme
- Membership in the HICS teacher community (ongoing support,
  annual gathering, shared resource repository)

Target: 30 teachers per cohort, 2 cohorts per year by Year 3.
Each trained teacher reaches ~150 students per year.
60 teachers → 9,000 students reached annually through the
teacher network alone.

First cohort: 2027.

`→ Register interest`
→ info@himalayansciences.org · Subject: Teacher development

---

### `/education/` index also links to:

**Scientific Computing Courses** — 4–6 week courses teaching
Python through real HICS data. Introduction · Signal Processing ·
Statistical Inference · Machine Learning · Research Computing.
Delivered in Kathmandu. NPR 3,000–5,000 per course with
scholarship slots. Revenue-generating from Year 1.

**Public Science Programme** — monthly public talks in Kathmandu,
free, Nepali language. Annual science festival. Live data
dashboards. Real-time environmental alerts accessible from
any phone.

---

## Page 11 — Open Knowledge (`/open-knowledge/`)

**Purpose:** Make explicit that HICS's outputs are not just for
enrolled students or partner institutions. Everything is public.
This page is a gateway, not a destination — it links to /data/
and /learn/ with framing that emphasises the open commitment.

Intro:

> HICS's public outputs exist for the world, not only for HICS's
> own programmes. All data is open. All instrument designs are
> open-source. All learning materials are freely available.
> Openness is not only ethical — it is the fastest path to
> credibility, collaboration, and impact.

Four sections:

**Live data and dashboards**

> Real-time public dashboards — live air quality, seismic activity,
> meteor detections, cosmic ray flux, and lightning strikes —
> accessible from any phone. No login required.
> `→ Data dashboard`

**Open datasets**

> Freely downloadable datasets in open formats with full
> documentation. Usable by any researcher, journalist, teacher,
> or government agency. CC BY 4.0 licence.
> `→ Download data`

**Open API**

> Programmatic access to all HICS data streams. For researchers,
> developers, and government agencies building tools on top of
> Nepal's environmental data.
> `→ API documentation`

**Open curricula and instrument designs**

> All HICS curriculum modules, instrument designs, firmware,
> and assembly documentation published openly. Any school,
> institution, or individual anywhere can download, build, teach,
> and adapt — with no restrictions.
> `→ Learning resources` · `→ GitHub: hics-nepal`

**Policy engagement** (text section, no link):

> HICS presents scientific data directly to government
> decision-makers: air quality data to Kathmandu Metropolitan City,
> seismic data to building code processes, atmospheric profiles to
> the Department of Hydrology and Meteorology. Science in service
> of decisions that affect the communities that generated the data.

**Offline-first** (text section):

> HICS's software platforms are designed for low-connectivity
> schools and remote research sites. Data is never lost because
> the internet is down. The IESH station logs locally and syncs
> when connected. Curriculum modules are downloadable PDFs that
> work without internet.

---

## Page 12 — Lab Notes Index (`/notes/`)

Intro:

> The lab notes are the working record of HICS — what was observed,
> what was built, what went wrong, what was found. Written as a
> scientist's notebook, not as a press release.

Filter tags: `observation` · `experiment` · `build` · `field` · `analysis`

Notes listed reverse-chronologically.
Each: date · tag · title · 2-sentence summary.

### First notes to publish at launch

**Note 1 — IESH v0 Build Log**
Type: `build` · Date: May 2026

> The first IESH environmental station built from a Raspberry Pi 3B,
> DHT22, and BMP280. Documents the build process, first readings,
> calibration issues (DHT22 reading 2°C high at high humidity),
> and the sync script to himalayansciences.org.
> Include: photo of hardware, first data chart, component list.

**Note 2 — Crystal Mountain School: Sensor Installation**
Type: `field` · Date: [installation date]

> Field dispatch from Dolpo — installing thermal sensors during
> construction of the passive solar multipurpose hall at Crystal
> Mountain School, 4,000m. What was installed, where, and why.
> Include: photos from site, sensor placement diagram, first readings.

**Note 3 — First Week of Atmospheric Data: KTM-001**
Type: `analysis` · Date: [one week after station goes live]

> What the first week of continuous atmospheric data from Kathmandu
> shows — the diurnal temperature cycle, the morning PM2.5 peak,
> the pressure pattern. What we expected, what surprised us.
> Include: charts from the first week's data.

---

## Page 11 — Learn (`/learn/`)

Intro:

> HICS's learning resources are freely available — for teachers,
> students, and anyone who wants to understand the science behind
> the instruments and data. Download them, use them, adapt them.

### Section A — Curriculum Modules

Each: title · grade level · linked instrument · summary · PDF download

**v1 modules to prepare:**

- _What is the atmosphere? Temperature, pressure, and altitude_
  Grades 8–10 · IESH · Explains what the sensors measure and why
- _Air quality: what is PM2.5 and why does it matter?_
  Grades 8–11 · IESH · Kathmandu Valley air quality as the case study
- _Passive solar: how do buildings stay warm without fuel?_
  Grades 9–11 · CMS project · The physics of thermal mass and solar gain

### Section B — Instrument Build Guides

Step-by-step guides. Each: difficulty · cost estimate · component list ·
assembly instructions · software setup · testing procedure.

**v1 guides to prepare:**

- _IESH v0: Environmental Monitor on Raspberry Pi_
  Difficulty: Moderate · Cost: ~NPR 5,000
  Full guide: wiring, Python code, Flask dashboard, sync script
- _DSLR Astrophotography: setup and first images_
  Difficulty: Easy · Cost: zero additional
  Camera settings, focusing at night, star trails
- _Diffraction Spectroscope: build for NPR 500_
  Difficulty: Easy · Cost: NPR 500–2,000
  Sodium streetlight spectrum as first target

### Section C — Scientific Computing

Python tutorials using real HICS data. Each links to a Jupyter notebook
downloadable from GitHub.

**v1 tutorials:**

- _Loading and plotting HICS CSV data in Python_
- _Time series analysis: finding patterns in atmospheric data_
- _Sensor calibration: cross-validating two temperature sensors_

---

## Page 12 — Contact (`/contact/`)

Simple, honest, direct. No contact form.
Four paths with pre-filled subject lines for email links.

**Research collaboration**

> If you are a researcher interested in working with HICS —
> visiting scientist, co-investigator, or data user —
> we want to hear about your work and how it connects to ours.
> → info@himalayansciences.org · Subject: Research collaboration

**Fellowships**

> Research fellowships for Nepali scientists and engineers
> who want to do serious science here, not abroad.
> → info@himalayansciences.org · Subject: Fellowship enquiry

**School partnerships**

> Instruments, data, residency programmes, and curriculum for schools.
> → info@himalayansciences.org · Subject: School partnership

**Everything else**
→ info@himalayansciences.org

Physical address: Lalitpur, Kathmandu, Nepal
Registration: Himalayan Institute For Contextual Sciences Pvt. Ltd.
Companies Act 2063 (2006)

---

## Content Priority — What to Build First

| #   | Item                        | Type            | Reason                      |
| --- | --------------------------- | --------------- | --------------------------- |
| 1   | Logo files in static        | Assets          | Needed for every page       |
| 2   | Home page                   | Page            | Front door                  |
| 3   | About page                  | Page            | Credibility                 |
| 4   | IESH instrument page        | Page            | Active, live data           |
| 5   | Atmospheric science         | Research page   | Active programme            |
| 6   | Building physics + CMS      | Research page   | Active + paper in progress  |
| 7   | Data page                   | Page            | Most important              |
| 8   | IESH build log              | Lab note        | Shows the work              |
| 9   | CMS sensor installation     | Lab note        | Active field work           |
| 10  | First week data analysis    | Lab note        | Data coming in              |
| 11  | Muon detector stub page     | Instrument page | In progress, PRD connection |
| 12  | Cosmic ray research stub    | Research page   | In progress                 |
| 13  | IESH build guide            | Learn           | Makes it replicable         |
| 14  | Planetarium instrument page | Instrument page | Vision, fundable            |
| 15  | Research index              | Page            | Links everything            |
| 16  | Learn index                 | Page            | Resources                   |
| 17  | Contact                     | Page            | Simple, needed              |

---

## Writing Tone — Reference

**Use this voice:**

> The DHT22 is reading approximately 2°C high compared to the BMP280
> at high humidity — a known issue with this sensor. We are logging
> both and will cross-calibrate against a reference when one is available.
> Both datasets are published raw; apply the offset if you need it.

> On the morning of [date], the PM2.5 proxy reading at KTM-001 spiked
> to 180% of the previous day's baseline between 07:00 and 09:00 —
> consistent with morning traffic and the brick kiln firing season.

**Never write this:**

> HICS is committed to advancing Nepal's scientific capacity through
> innovative approaches that leverage the unique geographical advantages
> of the region to generate impactful outputs for stakeholders.

The test: would a working scientist write this sentence in their notebook?
If yes: use it. If no: cut it.

---

## Key API Endpoints

| Endpoint                     | Method | Auth            | Purpose                    |
| ---------------------------- | ------ | --------------- | -------------------------- |
| `/api/data/latest/`          | GET    | None            | Latest reading per station |
| `/api/data/historical/`      | GET    | None            | Time series, N hours       |
| `/api/data/download/`        | GET    | None            | CSV download               |
| `/api/stations/`             | GET    | None            | All stations + status      |
| `/api/ingest/environmental/` | POST   | Station API key | Instrument sync            |

---

_This document defines Version 1 of himalayansciences.org._
_Scope is deliberately limited to what is real and active._
_Instruments and programmes not yet running appear only as planned,_
_never as present. Update this document as work progresses._

_Technical implementation: HICS_build_guide.md_
_Logo and design: HICS_website_plan.md_
