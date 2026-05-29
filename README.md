# Himalayan Institute for Contextual Sciences (HICS) Web Platform

[![Deploy to cPanel Production](https://github.com/hics-nepal/himalayansciences-web/actions/workflows/deploy.yml/badge.svg)](https://github.com/hics-nepal/himalayansciences-web/actions/workflows/deploy.yml)
[![Wagtail CMS](https://img.shields.io/badge/CMS-Wagtail%206.1.3-blue.svg)](https://wagtail.org/)
[![Django](https://img.shields.io/badge/Framework-Django%205.1.15-emerald.svg)](https://djangoproject.com/)
[![License](https://img.shields.io/badge/License-CERN%20OHL--W-orange.svg)](https://ohwr.org/cernohl)

Welcome to the official web platform of the **Himalayan Institute for Contextual Sciences (HICS)**. 

HICS is an independent, non-profit scientific research institute based in Kathmandu, Nepal. Our mission is **"Science rooted in place. Data open to all."** We specialize in high-altitude atmospheric sensing, cosmic ray tracking, and meteor astronomy. All of our custom-designed hardware (IESH nodes) is open source, and all scientific datasets are made available to the public in real-time.

---

## 🏔️ Core Features

*   **Wagtail CMS Power:** A robust and structured content management system for research programmes, lab notes, and instrumentation specifications.
*   **Custom Environmental Sensor Ingestion API:** High-reliability, token-authenticated POST endpoints (`/api/ingest/environmental/`) built for Raspberry Pi hardware nodes to sync local sqlite3 buffers to production MySQL databases.
*   **Real-time Public Data Streams:** Interactive public readouts (`/api/data/latest/`) and downloadable CSV files (`/api/data/download/`) for historical tracking.
*   **Dynamic Data Visualisations:** Seamless, lightweight vanilla JS and Chart.js integrations rendering local micro-climate fluctuations without heavy dependencies.
*   **Auto-Seeding Utility:** An advanced `seed_hics` management command that programmatically provisions pages, sets up HTTPS site-routing, and generates secure hardware tokens in one command.

---

## 🛠️ Technology Stack

*   **Backend:** Python 3.11 / Django 5.1.15 / Django REST Framework
*   **Content Management:** Wagtail 6.1.3 (optimized for stable deployment)
*   **Database:** MySQL / MariaDB (Production), SQLite (Local Dev)
*   **Caching:** Dynamic Local Memory Cache / Redis 
*   **Frontend:** Vanilla CSS (Tailwind-free), Vanilla Javascript, Chart.js
*   **Production Server:** Phusion Passenger WSGI on cPanel (NestNepal hosting)
*   **CI/CD:** Automated GitHub Actions SSH deployments

---

## 💻 Local Development Setup

To run the HICS website locally on your computer, follow these simple steps:

### 1. Clone the Repository
```bash
git clone https://github.com/hics-nepal/himalayansciences-web.git
cd himalayansciences-web
```

### 2. Configure Your Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Environment Variables
Copy the example environment file and customize your settings:
```bash
cp .env.example .env
```
Inside your `.env` file, set a secure `SECRET_KEY`, database credentials, and optional Redis parameters.

### 4. Apply Database Migrations
```bash
DJANGO_SETTINGS_MODULE=hics.settings.local python manage.py migrate
```

### 5. Seed the Wagtail Page Tree and default Station
Initialize the website structure, indexes, and register your first hardware station (`KTM-001`) dynamically:
```bash
DJANGO_SETTINGS_MODULE=hics.settings.local python manage.py seed_hics
```
*Note: Make sure to copy and save the generated **Station API Key** output by this command!*

### 6. Start the Development Server
```bash
DJANGO_SETTINGS_MODULE=hics.settings.local python manage.py runserver
```
Visit the local site at `http://127.0.0.1:8000/` and the Wagtail CMS panel at `http://127.0.0.1:8000/cms/`.

---

## 🚀 CI/CD & Production Deployment

The project is fully integrated with a GitHub Actions workflow (`.github/workflows/deploy.yml`) that triggers on every push to the `main` branch.

### Key Deployment Characteristics:
*   **Untracked Safe Pulls:** Automatically cleans Passenger cache files before git pulls to guarantee zero merge blockages.
*   **Secret Injection:** Injects cPanel MySQL passwords, database names, and Django secret keys securely at runtime.
*   **Passenger Integration:** Boots Phusion Passenger under a custom-configured `passenger_wsgi.py` in the web root.
*   **Dynamic LVE Activation:** Detects and activates the cPanel managed Python App virtualenv automatically.

### Production Commands
After a fresh production deployment, run the following commands via your cPanel terminal:

```bash
# Activate production environment
source /home/elyakadv/virtualenv/himalayansciences-web/3.11/bin/activate
cd /home/elyakadv/himalayansciences-web

# Build/update tables
DJANGO_SETTINGS_MODULE=hics.settings.production python manage.py migrate

# Seed base page trees and observation nodes
DJANGO_SETTINGS_MODULE=hics.settings.production python manage.py seed_hics

# Create administrative CMS user
DJANGO_SETTINGS_MODULE=hics.settings.production python manage.py createsuperuser
```

---

## 📈 Public API Specifications

| Endpoint | Method | Authentication | Description |
| :--- | :--- | :--- | :--- |
| `/api/data/latest/` | `GET` | Public | Returns the latest readings from active stations |
| `/api/data/historical/?hours=24` | `GET` | Public | Returns historical time-series data |
| `/api/data/download/` | `GET` | Public | Generates a downloadable CSV history |
| `/api/ingest/environmental/` | `POST` | Hardware Token | Accepts environmental parameters from IESH nodes |

---

## 🛡️ License

This project is licensed under the **CERN Open Hardware Licence Version 2 - Weakly Reciprocal (CERN-OHL-W)**. Software parts are licensed under the MIT License. Feel free to copy, modify, and distribute our hardware and software, provided modifications remain open source.

*Built with passion in Kathmandu, Nepal, for contextual and public scientific discovery.* 🏔️🛰️
