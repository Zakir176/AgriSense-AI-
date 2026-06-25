# AgriSense AI — Frontend

Vue 3 SPA built with Vite, Tailwind CSS, and Chart.js.

## Quick Start

```bash
npm install
npm run dev   # http://localhost:5173
```

Requires the backend API running on `http://localhost:8000`. See the [root README](../README.md) for full setup.

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start local dev server with HMR |
| `npm run build` | Production bundle → `dist/` |
| `npm run preview` | Preview the production build locally |

## Key Folders

```
src/
├── views/        # Page-level components (one per route)
├── components/   # Reusable UI components
├── services/
│   ├── api.js    # All fetch calls to the backend go through here
│   └── db.js     # IndexedDB offline cache (via idb)
└── router/       # Vue Router route definitions
```

## Environment

The API base URL is configured in `vite.config.js` via the `proxy` setting. For production builds, set `VITE_API_BASE_URL` in your deployment environment.

