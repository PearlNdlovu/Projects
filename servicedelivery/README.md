# CitizenFirst — Service Delivery Portal
### Setup Guide for Visual Studio Code

---

## Project Overview

**CitizenFirst** is a Django-based service delivery complaint portal built for South African citizens to report, track, and rate municipal service issues.

**Two Apps:**
- `mainapp` — Landing page, login/signup, anonymous access, chat API
- `reportapp` — Lodge complaint, track status, rate service, chat API

**GitHub Repository:**
> [https://github.com/yourusername/citizenfirst-portal](https://github.com/yourusername/citizenfirst-portal)
> *(Replace with your actual repository URL after uploading)*

---

## Screenshots

| Page | Description |
|------|-------------|
| `screenshot_home.png` | Landing page with hero, login/signup card, wheelbarrow worker |
| `screenshot_lodge.png` | Lodge a Complaint form with category selector and photo upload |
| `screenshot_track.png` | Track Complaint page with status circle tracker and chatbox |

---

## Navigation & Layout

**Navbar (all pages):**
- **Left:** CitizenFirst logo + brand name
- **Right:** Lodge a Complaint (gold button) | Login/Sign Up (purple button) | Help (dropdown — language switcher + contact links)

**Homepage (mainapp):**
- Hero section: large heading, subtitle, two CTA buttons, stats
- Auth card: tabbed Login / Register / Anonymous forms
- How It Works: 4-step process
- Quick Track: reference number search

**Lodge Complaint (reportapp):**
- Anonymous toggle, personal details, category grid, description, location, photo upload, notification preferences, submit

**Track Complaint (reportapp):**
- Reference number search, status circle tracker (5 stages), update timeline, contact channels, 5-star rating

**Chatbox:** Fixed bottom-right on all reportapp pages. Uses avatar from DiceBear API. Auto-replies to common questions.

---

## Step-by-Step Setup in VS Code

### Prerequisites
- Python 3.10 or later installed
- VS Code with the **Python** extension installed
- Git installed (optional but recommended)

---

### Step 1 — Open the project in VS Code

1. Open **Visual Studio Code**
2. Go to **File > Open Folder**
3. Select the `servicedelivery` folder (the one containing `manage.py`)
4. VS Code will open the project

---

### Step 2 — Create a virtual environment

Open the **integrated terminal** in VS Code:
- Go to **Terminal > New Terminal** (or press Ctrl + `)

In the terminal, type:

```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

---

### Step 3 — Install dependencies

With the virtual environment active, run:

```bash
pip install -r requirements.txt
```

This installs Django and Pillow (for image handling).

---

### Step 4 — Add the logo image

Place your logo image (the gardening tools image) in:

```
static/images/logo.png
```

The navbar and footer both use this file. The filename must be exactly `logo.png`.

---

### Step 5 — Run database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the SQLite database file (`db.sqlite3`) and all required tables.

---

### Step 6 — Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password. This gives you access to `/admin/`.

---

### Step 7 — Run the development server

```bash
python manage.py runserver
```

Open your browser and go to:

```
http://127.0.0.1:8000/
```

---

### Step 8 — Access the Admin panel

Go to:

```
http://127.0.0.1:8000/admin/
```

Log in with your superuser credentials. From here you can:
- View, edit, and update all complaints
- Change complaint status (triggers timeline updates automatically)
- Manage users, chat messages, and ratings

---

## URL Structure

| URL | View | Description |
|-----|------|-------------|
| `/` | `mainapp.views.home` | Landing page, login, signup |
| `/logout/` | `mainapp.views.logout_view` | Logout user |
| `/api/chat/` | `mainapp.views.chat_api` | Home page chat API |
| `/report/lodge/` | `reportapp.views.lodge_complaint` | Lodge complaint form |
| `/report/success/<ref>/` | `reportapp.views.complaint_success` | Submission confirmation |
| `/report/track/` | `reportapp.views.track_complaint` | Track complaint status |
| `/report/rate/` | `reportapp.views.submit_rating` | Submit star rating |
| `/report/api/chat/` | `reportapp.views.report_chat_api` | Report pages chat API |
| `/admin/` | Django Admin | Admin dashboard |

---

## Project Structure

```
servicedelivery/
├── manage.py
├── requirements.txt
├── db.sqlite3                  (created after migrate)
├── servicedelivery/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── mainapp/                    App 1
│   ├── models.py               ChatMessage
│   ├── views.py                home, logout, chat_api
│   ├── urls.py
│   ├── admin.py
│   └── templates/mainapp/
│       └── home.html
├── reportapp/                  App 2
│   ├── models.py               Complaint, ComplaintUpdate, Rating
│   ├── views.py                lodge, track, rate, chat
│   ├── urls.py
│   ├── admin.py
│   └── templates/reportapp/
│       ├── lodge_complaint.html
│       ├── complaint_success.html
│       └── track_complaint.html
├── templates/
│   └── base.html               Shared navbar, footer, messages
├── static/
│   ├── css/
│   │   └── global.css
│   └── images/
│       └── logo.png            (add your logo here)
└── media/
    └── uploads/                (complaint photos stored here)
```

---

## Features Implemented

- User registration and login with Django's auth system
- Anonymous complaint submission (no personal data stored)
- Unique reference number generated on submission (e.g. SD-2024-ABC123)
- 8 complaint categories with icon grid selector
- Photo upload for complaints
- 5-stage status tracker (Pending, Submitted, In Progress, Resolved, Closed)
- Update timeline per complaint
- 5-star rating system for resolved complaints
- Live chatbox with auto-replies on lodge and track pages
- Avatar from DiceBear API for chat agent
- Language switcher in Help dropdown (English, Zulu, Xhosa, Afrikaans, Sotho)
- WhatsApp, phone, and email contact options on tracking page
- Admin panel with inline update history and status-change tracking
- Fully responsive design (mobile-friendly)
- Animated success messages that auto-dismiss
- Scroll animations on page load

---

## Editing in Django Admin

1. Go to `http://127.0.0.1:8000/admin/`
2. Click **Complaints**
3. Click any complaint to open it
4. Change the **Status** field (e.g. from Submitted to In Progress)
5. Click **Save** — the system automatically logs the status change in the complaint's update timeline

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'django'` | Activate your virtual environment: `venv\Scripts\activate` |
| Logo not showing | Make sure `logo.png` is in `static/images/logo.png` and run `python manage.py collectstatic` |
| Images not uploading | Check that the `media/uploads/` folder exists |
| Port already in use | Run on a different port: `python manage.py runserver 8080` |
| Database errors | Delete `db.sqlite3` and re-run `python manage.py migrate` |
