<div align="center">

# 🌱 AgriSense AI

**Smart Poultry Farm Management — Built for African Smallholder Farmers**

[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Python%203.11-009688?style=flat-square&logo=fastapi)](./backend)
[![Frontend](https://img.shields.io/badge/Frontend-Vue%203%20%2B%20Vite-42b883?style=flat-square&logo=vue.js)](./frontend)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2015-336791?style=flat-square&logo=postgresql)](./docker-compose.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](./LICENSE)

</div>

---

## 📖 What is AgriSense AI?

AgriSense AI is an **offline-first, mobile-friendly farm management dashboard** built specifically for smallholder poultry farmers in Sub-Saharan Africa. The pilot farm is **Prime Nest Poultry Farm, Lusaka, Zambia** (Evans Kabwe).

Rather than relying on expensive consultants or paper logbooks, farmers and their operators can:

- **Log daily feed & water consumption** and get instant AI-powered anomaly alerts
- **Track flock growth** against industry weight benchmarks (Cobb 500 / Ross 308 curves)
- **Record the full medication and vaccination schedule** for each batch
- **View analytics** — weekly summaries, batch comparisons, and cost trend charts
- **Run AI visual monitoring** — upload coop video footage for bird-count estimation and movement scoring (YOLOv8-powered)
- **Record and analyse audio** — detect distress calls and abnormal sounds in the coop

The system is designed to run on **low-cost Android tablets or a desktop browser**, with IndexedDB caching so it keeps working during power outages or patchy internet.

---

## 🏗️ Architecture

```
AgriSense-AI/
├── backend/               # Python FastAPI REST API
│   ├── app/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── routers/       # API route handlers (one file per resource)
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   └── services/      # Business logic (rules engine, AI inference)
│   ├── seed_data.py       # Demo data seeder (Evans' real farm data)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/              # Vue 3 SPA (Vite + Tailwind CSS)
│   ├── src/
│   │   ├── views/         # Page-level components
│   │   ├── components/    # Reusable UI components
│   │   ├── services/      # API client + IndexedDB layer
│   │   └── router/        # Vue Router config
│   └── vite.config.js
│
└── docker-compose.yml     # PostgreSQL 15 dev database
```

### Key Tech Choices

| Layer | Technology | Why |
|---|---|---|
| API | **FastAPI** | Fast async Python, auto-generates OpenAPI docs at `/docs` |
| Database | **PostgreSQL 15** | Relational, handles batch/time-series data cleanly |
| ORM | **SQLAlchemy 2** | Type-safe models, easy migrations |
| Frontend | **Vue 3** (Composition API) | Lightweight, great for offline-capable SPAs |
| Charts | **Chart.js 4** | Zero-dependency, works offline |
| AI Vision | **Ultralytics YOLOv8** | Bird detection & counting from video frames |
| Auth | **JWT (HS256)** | Single-operator model, 24-hour tokens |
| Offline | **IndexedDB (idb)** | Cache reads/writes locally for low-connectivity use |

---

## ⚙️ Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **npm** | 9+ | bundled with Node |
| **Docker Desktop** | any recent | [docker.com](https://www.docker.com/products/docker-desktop/) *(for Postgres)* |
| **Git** | any | [git-scm.com](https://git-scm.com/) |

> **No Docker?** You can also install PostgreSQL locally — just make sure the `DATABASE_URL` in your `.env` matches your local config.

---

## 🚀 Local Development Setup

### 1 — Clone the repo

```bash
git clone https://github.com/Zakir176/AgriSense-AI-.git
cd AgriSense-AI-
```

### 2 — Start the database

```bash
docker-compose up -d
```

This spins up **PostgreSQL 15** on `localhost:5432` with:
- User: `postgres`
- Password: `postgrespassword`
- Database: `agrisense`

### 3 — Set up the backend

```bash
cd backend

# Create & activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# (Edit .env if your DB credentials differ from the defaults)
```

#### Seed demo data (Evans' real farm data)

```bash
python seed_data.py
```

This populates the database with:
- **Prime Nest Poultry Farm** (Lusaka, Zambia)
- **2 batches** of 200 Cobb 500 birds (1 active at Day 22, 1 archived full cycle)
- **42 daily feed & water readings** per batch, with a realistic Day-15 anomaly
- **Weekly growth samples** against a standard Cobb 500 weight curve
- **6 medication / vaccination entries** (Marek's → Newcastle → Gumboro → Vitamins → Amoxicillin)
- **3 alerts** (critical, warning, info)

#### Start the API server
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be live at:
- **http://localhost:8000** — root health check
- **http://localhost:8000/docs** — interactive Swagger UI (great for exploring endpoints)
- **http://localhost:8000/api/v1** — all REST endpoints

**Default login credentials** (seeded automatically on first startup):
| Field | Value |
|---|---|
| Username | `operator` |
| Password | `prime_nest_2026` |

### 4 — Set up the frontend

Open a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

The app will be live at **http://localhost:5173**

---

## 📡 API Reference

All endpoints are prefixed with `/api/v1`. Full interactive docs available at `/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | Obtain JWT access token |
| `GET` | `/farms/` | List all farms |
| `GET/POST` | `/batches/` | List or create batches |
| `GET/POST` | `/readings/` | Feed & water log entries |
| `GET` | `/readings/summary` | Weekly/monthly aggregate stats |
| `GET/POST` | `/growth/` | Growth weight samples |
| `GET/POST` | `/medications/` | Medication & vaccine log |
| `GET` | `/alerts/` | System-generated anomaly alerts |
| `PATCH` | `/alerts/{id}/acknowledge` | Mark an alert as read |
| `POST` | `/inference/upload` | Upload video for AI bird-count analysis |

### How anomaly detection works

When a new feed/water reading is saved, `rules_engine.py` automatically:
1. Fetches the **7-day rolling average** for that batch
2. If the new reading deviates by **more than 20%** in either direction → flags it as abnormal and creates an `Alert`
3. Also flags **high mortality events** if daily deaths exceed 0.5% of the initial flock

---

## 🗂️ Database Models

```
Farm ──< Batch ──< FeedWaterReading
                ├─< GrowthSample
                ├─< MedicationEntry
                ├─< Alert
                └─< MediaClip ──< InferenceResult
```

| Model | Key Fields |
|---|---|
| `Farm` | `name`, `location` |
| `Batch` | `farm_id`, `start_date`, `bird_count`, `breed`, `status` |
| `FeedWaterReading` | `batch_id`, `date`, `feed_kg`, `water_litres`, `mortality_count`, `flagged_abnormal` |
| `GrowthSample` | `batch_id`, `date`, `avg_weight_g`, `sample_size` |
| `MedicationEntry` | `batch_id`, `date`, `medicine_type`, `dosage`, `outcome_note` |
| `Alert` | `batch_id`, `type`, `message`, `severity`, `acknowledged` |
| `MediaClip` | `batch_id`, `file_url`, `uploaded_at` |
| `InferenceResult` | `media_clip_id`, `bird_count_est`, `movement_score`, `low_activity_windows` |

---

## 🖥️ Frontend Pages

| Route | View | Description |
|---|---|---|
| `/login` | `Login.vue` | JWT authentication screen |
| `/` | `Dashboard.vue` | Overview — key metrics, recent alerts, batch status |
| `/batches` | `Batches.vue` | Batch management — create, archive, view history |
| `/feed-water` | `FeedWater.vue` | Daily feed & water log + anomaly timeline |
| `/growth` | `Growth.vue` | Weight tracking vs. Cobb 500 benchmark curve |
| `/medications` | `Medications.vue` | Full vaccination & medication schedule |
| `/analytics` | `Analytics.vue` | Multi-batch comparison, cost trends, weekly reports |
| `/visual-monitor` | `AIVisualMonitor.vue` | Upload coop video → get bird count + movement score |
| `/audio-insight` | `AudioInsight.vue` | Record/upload coop audio → distress call detection |

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full guide. Short version:

1. **Fork** the repo and create a branch: `git checkout -b feat/your-feature-name`
2. Make your changes and write clear commit messages
3. Open a **Pull Request** with a description of what you changed and why
4. A maintainer will review and merge

> Please check the open [Issues](https://github.com/Zakir176/AgriSense-AI-/issues) before starting work — pick up something from the backlog or discuss a new idea there first.

---

## 📋 Roadmap

- [ ] **SMS/WhatsApp alert delivery** (Twilio / Africa's Talking)
- [ ] **Mobile-native wrapper** (Capacitor.js for Android APK)
- [ ] **Multi-farm / multi-user support** with role-based access
- [ ] **Batch cost tracking** — feed cost per kg of bird weight, profitability report
- [ ] **Flock mortality heatmap** — visualise death patterns over time
- [ ] **YOLOv8 fine-tuning** on local Zambian coop footage for better accuracy
- [ ] **Swahili / Nyanja UI localisation**

---

## 📄 License

MIT © 2026 AgriSense AI Contributors
