# NUDGE frontend

React 19 + Vite. From Messages to Actions: the student life management platform.

## Design

Figma file with the prototype, components and mood board:
[NUDGE-PROJECT on Figma](https://www.figma.com/design/BK3CHWwcyt51jlTZP3Wblz/NUDGE-PROJECT)

## Run it

```
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # production build in dist/
npm run lint
```

## Current state

- Sign in is in **demo mode** (browser storage). There is no login in the backend yet, so passwords are not checked.
- **Tasks use the real backend** (list, add, edit title/date/time, change status, delete) when `frontend/.env` contains the API address. Without it, the app runs on sample data.
- Still sample or stand-ins until those modules are connected to the API: message parsing, screenshot upload, priorities and analytics.
- All data calls go through `src/services/` and `src/lib/apiClient.js`.

## Run it with the backend

1. In the repo root (needs the `backend/` folder from `feature/rumana-data`):
   ```
   pip install -r backend/requirements.txt
   python -m backend.database.build_database --db-path data\nudge.db --parser-snapshot data\samples\real\parser_snapshot.json --ocr-snapshot data\samples\real\ocr_snapshot.json
   python -m backend.api
   ```
   The API runs at http://127.0.0.1:8000 and only accepts requests from http://localhost:5173.
2. In `frontend/`, copy `.env.example` to `.env`, then run `npm run dev`.

To go back to sample data, delete `frontend/.env` and restart `npm run dev`.

## Media

The landing hero uses `public/media/nudge-hero.mp4`, `nudge-hero.webm` and `nudge-hero-poster.jpg`, plus six card images (`messages`, `deadline`, `priorities`, `calendar`, `clashes`, `coursework`, all `.png`). Keep them small.
