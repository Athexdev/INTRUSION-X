# INTRUSION X - Network Intrusion Detection System (SOC Dashboard)

Welcome to the **INTRUSION X** Master Security Operations Center (SOC) dashboard. This project is a dark, cyber-themed, fully responsive NIDS backend interface built with Django. It features a seamless login integration via a dynamic 3D-globe landing page, live threat monitoring dashboards, interactive network traffic charts, alert visualizations, and more.

## Architecture & Stack
- **Backend framework**: Django (Python)
- **Database**: SQLite3 (default)
- **Frontend Assets**: Three.js, GSAP (animations), Chart.js (graphs), TailwindCSS (utility layouts), Custom Vanilla CSS (Cyber Theme & Glassmorphism)

## Workspace Architecture
```text
NIDS_BACKEND/
│
├── dashboard/        # Core SOC interface, metrics logic, and system settings
├── users/            # Handles root authentication, security, and credentials
├── detection/        # Processing logic models (Network logs, Alerts)
├── static/           # Global CSS and JavaScripts logic (landing.js, style.css)
├── templates/        # Global unified templates (landing.html, base.html)
└── nids_project/     # Django root settings and URL routing configs
```

## Quick Start Guide

### 1. Requirements
Ensure you have Python 3.8+ installed. Install the necessary packages.
```bash
pip install django
```
*(If you have a `requirements.txt` file, use `pip install -r requirements.txt`)*

### 2. Database Migrations
Before booting up the server for the first time (or after any model updates), you must securely apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Creating an Admin Account (SOC Operator)
To access the dashboard, you will need a root clearance credential. 
```bash
python manage.py createsuperuser
```
Follow the interactive prompts to assign a Username (Identifier) and Password (Clearance Key).

### 4. Booting the Application
Execute the following to start the master control server:
```bash
python manage.py runserver
```
Once the server initiates, go to **`http://127.0.0.1:8000/`** safely in your browser. 
You will be greeted by the `INTRUSION X` live landing page. Use your configured Admin credentials to securely initialize your session into the SOC dashboard.

## Additional Master Commands

**Collect Static Assets**
When moving to a production environment, gather all theme files across modules safely:
```bash
python manage.py collectstatic
```

**Execute Custom Helper Scripts**
The root directory includes automated Python files that can be run out-of-band depending on your operational needs:
```bash
# To check basic operational logic statuses
python ATHEX_SOC.py

# Auto-execute migrations securely via local script
python run_migrations.py

# Reset or configure the project directory structures
python debesh_help.py
```

## Aesthetic Notes
The platform features a native "Terminal Glow" glassmorphism utilizing specifically tailored CSS tokens. Modifying core colors globally should ideally only require overriding the CSS Custom Properties in `:root` inside `static/css/style.css` and `static/css/landing.css`. The font family stack is anchored by the *JetBrains Mono* font.
