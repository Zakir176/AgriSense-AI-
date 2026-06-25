# 🤝 Contributing to AgriSense AI

Thank you for your interest in contributing! This guide covers everything you need to get up and running as a contributor.

> First time contributing to open source? Check out [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/).

---

## 📋 Table of Contents

- [Before You Start](#-before-you-start)
- [Development Setup](#-development-setup)
- [Branch Naming](#-branch-naming)
- [Commit Messages](#-commit-messages)
- [Code Style](#-code-style)
- [Opening a Pull Request](#-opening-a-pull-request)
- [Project Structure Cheatsheet](#-project-structure-cheatsheet)
- [Where to Get Help](#-where-to-get-help)

---

## 🔎 Before You Start

1. **Check the [Issues](https://github.com/Zakir176/AgriSense-AI-/issues) tab first.** Someone may already be working on the same thing.
2. **Open an Issue** before starting significant work — this avoids duplicated effort and lets maintainers give early feedback.
3. **Assign yourself** to an Issue or leave a comment saying you're picking it up.

---

## 💻 Development Setup

Follow the [README.md](./README.md#-local-development-setup) to get your local environment running. Once that's done, come back here.

### Running tests

> ⚠️ Automated tests are on the roadmap. For now, manual verification is expected for PRs. See the [PR checklist](#-opening-a-pull-request) below.

---

## 🌿 Branch Naming

Use this naming pattern when creating a branch:

```
<type>/<short-description>
```

| Type | When to use |
|---|---|
| `feat/` | A new feature (e.g. `feat/sms-alerts`) |
| `fix/` | A bug fix (e.g. `fix/growth-chart-axis`) |
| `docs/` | Documentation only (e.g. `docs/api-reference`) |
| `refactor/` | Code restructuring with no behaviour change |
| `chore/` | Dependency updates, config, tooling |
| `data/` | Changes to seed data or migrations |

**Examples:**
```
feat/batch-cost-tracking
fix/alert-acknowledge-endpoint
docs/mobile-setup-guide
```

---

## ✍️ Commit Messages

We follow a simplified [Conventional Commits](https://www.conventionalcommits.org/) style:

```
<type>: <short imperative summary>

Optional longer description explaining why, not what.
```

**Good examples:**
```
feat: add 7-day rolling average to growth chart
fix: correct water_litres null check in rules engine
docs: add Docker setup instructions to README
chore: upgrade Chart.js to v4.5.1
data: update seed_data with Evans' Week 4-6 actuals
```

**Rules:**
- Use the **imperative mood** — "add" not "added" or "adds"
- Keep the summary line under **72 characters**
- Reference an Issue number when applicable: `fix: resolve feed dip flag (#42)`

---

## 🎨 Code Style

### Backend (Python)

- **Python 3.11+**, typed where practical
- Follow [PEP 8](https://peps.python.org/pep-0008/)
- All new API routes go in `backend/app/routers/` — one file per resource
- All business logic (anomaly rules, inference, etc.) goes in `backend/app/services/`
- New database tables need a **model** in `models/` and a **schema** in `schemas/`
- Do **not** add database migration logic inline — keep schema changes in models and document them in your PR

```python
# Good — clear types, docstring, focused function
def check_feed_anomaly(db: Session, batch_id: int, feed_kg: float) -> bool:
    """Returns True if feed_kg deviates >20% from the 7-day rolling average."""
    ...

# Avoid — no types, unclear name
def check(db, id, f):
    ...
```

### Frontend (Vue 3 / JavaScript)

- Use the **Composition API** (`<script setup>`) — not Options API
- One `.vue` file per page/component; keep components under ~300 lines
- API calls go through `src/services/api.js` — never call `fetch()` directly from a component
- Offline caching logic goes in `src/services/db.js` (IndexedDB via `idb`)
- Use **Tailwind CSS** utility classes for styling
- Keep Chart.js chart configs co-located in the component that renders them

```vue
<!-- Good -->
<script setup>
import { ref, onMounted } from 'vue'
import { getReadings } from '@/services/api'

const readings = ref([])
onMounted(async () => { readings.value = await getReadings() })
</script>

<!-- Avoid: calling fetch() directly in a component -->
```

---

## 🔀 Opening a Pull Request

1. **Push your branch** and open a PR against `main`
2. Fill in the PR template (title, description, linked Issue)
3. **Check all items in this list before requesting review:**

```
PR Checklist

Backend changes:
[ ] New endpoints are documented in the README API table
[ ] Rules engine / business logic is in services/, not in routers/
[ ] .env.example is updated if new env vars are added
[ ] seed_data.py is updated if new models were added

Frontend changes:
[ ] New page is registered in src/router/
[ ] API calls go through src/services/api.js
[ ] The page works when the backend is offline (graceful fallback)
[ ] No hardcoded localhost URLs left in component files

Both:
[ ] The app still runs: uvicorn + npm run dev both start without errors
[ ] No debug console.log() or print() statements left in
[ ] Commit messages follow the Conventional Commits format
```

---

## 📁 Project Structure Cheatsheet

```
AgriSense-AI/
│
├── backend/
│   ├── app/
│   │   ├── models/          ← Add new DB tables here (SQLAlchemy models)
│   │   ├── schemas/         ← Add request/response shapes here (Pydantic)
│   │   ├── routers/         ← Add new API endpoints here
│   │   └── services/        ← Add business logic here (rules engine, AI)
│   ├── seed_data.py         ← Update when adding new models/demo data
│   ├── requirements.txt     ← Update when adding new Python packages
│   └── .env.example         ← Update when adding new env variables
│
├── frontend/
│   ├── src/
│   │   ├── views/           ← Add new pages here
│   │   ├── components/      ← Add shared UI components here
│   │   ├── services/
│   │   │   ├── api.js       ← All backend API calls go through here
│   │   │   └── db.js        ← IndexedDB offline caching logic
│   │   └── router/          ← Register new routes here
│   └── package.json         ← Update when adding new npm packages
│
├── docker-compose.yml       ← PostgreSQL dev database config
├── README.md                ← Project overview & setup guide
└── CONTRIBUTING.md          ← This file
```

---

## ❓ Where to Get Help

- **Bug or question?** Open a [GitHub Issue](https://github.com/Zakir176/AgriSense-AI-/issues)
- **API exploration?** Run the backend and visit **http://localhost:8000/docs** — the Swagger UI documents every endpoint interactively
- **Database schema questions?** Check `backend/app/models/` and the ERD in the README
- **Stuck on setup?** Paste your error in a new Issue and someone will help

---

*Thanks for helping bring better tools to African smallholder farmers. 🌍*
