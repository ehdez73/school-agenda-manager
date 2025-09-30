# Frontend (React + Vite) for Agenda

This folder contains the single-page frontend for the Agenda scheduling application. It's built with React and Vite and intended to be run locally during development or packaged into the project's Docker Compose setup.

This README covers the most common tasks: getting the frontend running, available scripts, an overview of the folder structure, styling conventions, and troubleshooting tips.

## Quick start (local development)

Requirements:
- Node.js 18+ (recommended)
- npm or yarn

Install dependencies and start the dev server:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser (Vite will print the exact URL). The frontend is configured for hot module replacement (HMR) during development.

## Available scripts
Run these from the `frontend` folder.

- npm run dev — Start Vite dev server (HMR).
- npm run build — Create a production build in `dist/`.
- npm run preview — Locally preview a production build.
- npm run lint — Run ESLint (if configured) to check code style.

If your environment prefers Yarn, replace `npm` with `yarn` and `npm run <script>` with `yarn <script>`.

## Integration with backend

The repo contains a backend service in `backend/` that provides the API and scheduler. During development you can run the backend locally and point the frontend to it by updating the API base URL in `frontend/src/lib` (look for environment variables or the file that exports the API root). When using Docker Compose the frontend and backend services are wired together.

## Project structure (important files)

- `index.html` — App entry HTML used by Vite.
- `src/main.jsx` — App bootstrapping and global providers.
- `src/App.jsx` — Top-level routes and layout.
- `src/components/` — React components used across the app (forms, lists, modals, timetable renderer).
- `src/styles/` — Global and shared styles.
- `src/i18n/` — Translation resources.
- `public/` — Static assets served as-is.
- `STYLING_GUIDE.md` — Frontend styling conventions (colors, spacing, component patterns). Follow it when adding or modifying CSS.

Look for components mentioned in the repository root README or in backend endpoints when implementing new UI features.

## Styling

Follow `STYLING_GUIDE.md` for CSS patterns and conventions. The project prefers small, focused CSS files next to components and uses simple class-based styles. Keep styles reusable and avoid global overrides when possible.

## Environment variables

Vite supports environment files named `.env`, `.env.development`, `.env.production`. Common variables:
- VITE_API_BASE — Base URL for the backend API (e.g. `http://localhost:5000/api`).

Create a `.env.local` or `.env` file in `frontend/` for local overrides. Do not commit secrets.

## Building and previewing production

```bash
cd frontend
npm run build
npm run preview
```

This produces optimized static assets in `frontend/dist/` which can be served by any static server or included in Docker images.

## Docker / Docker Compose

The repository includes a `docker-compose.yml` at the repo root that can run the full stack. If you prefer to run only the frontend container, the `frontend/Dockerfile` is available; consult the compose file for service names and network configuration.

## Troubleshooting

- If HMR doesn't update, clear the browser cache and restart `npm run dev`.
- If dependency install fails on Apple Silicon, try `npm rebuild` or use Node 18 LTS via nvm: `nvm install 18 && nvm use 18`.
- If the frontend can't reach the API, ensure the backend is running and `VITE_API_BASE` is configured correctly.

## Contributing

When adding UI functionality:
- Create or update components in `src/components/`.
- Add styles in `src/styles/` or component-level CSS.
- Keep changes small and add tests where appropriate.

Follow the project's coding conventions and run the linter before opening a PR.

## Where to go next

- For backend integration and the scheduling model, see `backend/README.md` (or `README.md` at repo root).
- For styling rules, open `STYLING_GUIDE.md` in this folder.

If you'd like, I can also add small developer helper scripts (e.g., an npm script to proxy API to the backend during dev) or a minimal `.env.example` for common variables. Tell me which you'd prefer.
