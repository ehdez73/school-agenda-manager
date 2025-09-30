# Agenda — Scheduling app

This repository is a pet project created to tackle a constraint programming problem using Google OR-Tools in a "vibe coding" style — exploratory, iterative, and playground-driven development. The goal is to model school timetabling constraints (teachers, groups, subjects, and timeslots) and experiment with CP-SAT to find feasible weekly schedules.

This repository contains a small web application that generates weekly timetables for a school. It includes:

- A Python/Flask backend that models courses, subjects and teachers and uses OR-Tools CP-SAT to generate timetables.
- A React + Vite frontend that renders and edits courses, teachers, and the generated timetable.
- Convenience tooling and Docker Compose configuration to run the full stack locally.

This README gives a quick orientation and the recommended developer workflow.

## Repo layout

- `backend/` — Flask app, scheduler, DB models, restrictions and tests. See `backend/README.md` for details.
- `frontend/` — React + Vite SPA. See `frontend/README.md` and `frontend/STYLING_GUIDE.md`.
- `docker-compose.yml` — Full stack compose file to run frontend + backend.

## Recommended local workflow (uv-first)

This repo uses the `uv` helper script to manage environments and run commands consistently across contributors and CI. Follow this pattern on macOS/Linux/Windows Subsystem for Linux:

1. Sync the environment (this will create/update `.venv` and install dependencies):

```bash
cd backend
uv sync
```

2. Run the backend (in the backend folder):

```bash
uv run flask --app app.py run --host 0.0.0.0 --port 5000 --debug
```

3. Run the frontend (from `frontend/`):

```bash
cd frontend
npm install
npm run dev
```

## Docker Compose

To run the entire stack with Docker (no local Python/npm installs required):

```bash
docker compose up --build
```

This will start the backend and frontend services and make the frontend available on the port configured in the compose file.

## Tests

Backend tests (use `uv`):

```bash
cd backend
uv run python -m pytest -q
```

## Where to look

- Backend core: `backend/models.py`, `backend/scheduler.py`, `backend/restrictions/`.
- Frontend core: `frontend/src/components/`, `frontend/src/lib/`, `frontend/STYLING_GUIDE.md`.
- DB: `agenda.db` (repo root) — use `backend/populate_db.py` to recreate seed data.

## Contributing

- Write small, focused PRs. When adding restrictions, follow the pattern in `backend/restrictions/` and add a unit test under `backend/test/restrictions/`.
- Keep frontend style changes consistent with `frontend/STYLING_GUIDE.md`.
