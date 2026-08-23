# 🩸 LifeLink — Critical Care Coordination Platform
> **Right Blood. Right Medicine. Right Time.**

LifeLink is a specialized critical-care coordination platform built to solve acute supply and timing bottlenecks for chronic and emergency patients (e.g., Thalassemia transfusion cycles, Chemotherapy platelet schedules, rare blood reservation, and caregiver coordination).

---

## 🌟 Key Features

- **🔴 Verified Live Blood Grid & Reservation**: Real-time component-level inventory (PRBC, Platelets, FFP, Whole Blood) across regional blood banks with 2-hour emergency reservation lock and verification audit trail.
- **💊 Critical Medicine Supply & Depletion Forecaster**: Live availability tracking for critical medications (Deferasirox, Hydroxyurea, Filgrastim, Paclitaxel) with automatic depletion countdowns.
- **📅 Patient Treatment Timeline**: 21-day recurring transfusion cycles and chemotherapy chemo-milestone trackers with proactive automated alerts.
- **🛡️ Caregiver Circle**: Instant escalation, WhatsApp alerts, and emergency broadcast dispatch to designated caregivers and hospital teams.
- **🤖 AI Clinical Intelligence Assistant**: Personalized daily care briefings, risk scorings, and clinical guideline explanations.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Modern Web Browser

### 1. Setup & Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd lifelink

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Run the Server
```bash
# From the backend directory:
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

### 3. Open in Browser
- **Web Application**: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- **API Health Check**: [http://127.0.0.1:8080/health](http://127.0.0.1:8080/health)

---

## 👥 Demo Personas

| Role | Email | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Patient (Thalassemia)** | `priya@example.com` | `patient123` | Transfusion tracking, blood reservation |
| **Patient (Chemotherapy)** | `arjun@example.com` | `patient123` | Platelet alerts, oncology milestones |
| **Blood Bank Staff** | `bank@lifelink.org` | `admin123` | Real-time stock updates & reservation dispatch |
| **Emergency Coordinator** | `admin@lifelink.org` | `admin123` | System oversight & emergency broadcasts |

---

## 📂 Project Structure

```
lifelink/
├── backend/
│   ├── app/
│   │   ├── api/            # REST API route handlers
│   │   ├── database/       # DB session & initial seed data
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Core business & matching logic
│   │   ├── config.py       # Configuration settings
│   │   └── main.py         # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── tests/              # Backend test suite
├── frontend/
│   ├── css/
│   │   └── styles.css      # Custom UI theme and glassmorphism styling
│   ├── js/
│   │   ├── api.js          # API connector client
│   │   ├── app.js          # Application controller & view switcher
│   │   ├── map.js          # Leaflet map integration
│   │   ├── state.js        # Global client state management
│   │   └── killer_demo.js  # Interactive scenario runner
│   └── index.html          # Single-page interface
├── .gitignore
└── README.md
```

---

## 📄 License
MIT License
