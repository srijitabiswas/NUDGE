
# NUDGE frontend

React 19 + Vite. From Messages to Actions: the student life management platform.

## Run it

```
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # production build in dist/
npm run lint
```

## Current state

- Sign in and the task data run in **demo mode** (browser storage and sample data). Nothing is sent to a server and passwords are not checked.
- All data calls go through `src/services/` and `src/lib/apiClient.js`. To connect the real backend, add `frontend/.env` with `VITE_API_BASE_URL=<backend address>`, then set `USING_DEMO_AUTH` and `USING_SAMPLE_DATA` to `false` and implement the functions in `authService.js` and `taskService.js`.
- Set the contact email in `src/config.js`.

## Media

The landing hero uses `public/media/nudge-hero.mp4`, `nudge-hero.webm` and `nudge-hero-poster.jpg`, plus six card images (`messages`, `deadline`, `priorities`, `calendar`, `clashes`, `coursework`, all `.png`). Keep them small.