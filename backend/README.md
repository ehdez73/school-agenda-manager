# Agenda — Backend

This folder contains the backend for the Agenda scheduling application. It is a small Flask app that uses a SQLite database and OR-Tools CP-SAT to build weekly timetables respecting teacher availability, subject weekly hours, and other constraints.

This README summarizes how to set up the development environment, run the server, populate the database, run the scheduler, run tests, and where to look when you want to extend the system (for example adding a new scheduling restriction).

## Contents
# Agenda — Backend

This folder contains the backend for the Agenda scheduling application. It is a Flask app that uses a SQLite database and OR-Tools CP-SAT to build weekly timetables respecting teacher availability, subject weekly hours, and other constraints.

This README explains how to set up the development environment using the repository helper `uv`, run the server, populate the database, execute the scheduler, run tests, and where to find extension points.

## Contents

- `app.py` — Flask application entrypoints / routes registration.
- `models.py` — SQLAlchemy ORM models used across the project (Course, Subject, Teacher, Activity, Timeslot, etc.).
- `scheduler.py` — Builds the OR-Tools CP-SAT model, wires restrictions, and saves Activities/Timeslots to the DB.
- `restrictions/` — Individual restriction classes (each implements a `apply(...)` method and has unit tests).
- `populate_db.py` — Helper script to seed the SQLite DB for local testing.
- `timetable.py` — Markdown/printable timetable generator used by the frontend.
- `schemas.py` — Pydantic (v2) schemas for response serialization.
- `Dockerfile` — Container definition for running the backend in Docker.
- `pyproject.toml` — Python packaging and dependency metadata.

## Quickstart — development (uv-only)

Prerequisites:
- Python 3.13+ (recommended) or a supported 3.x version present in `pyproject.toml`.
- Git (to clone/update the repo).

All environment creation, dependency installation and execution must be done with the repository helper `uv`. Do not run `python -m venv`, `pip install` or similar commands directly here — use `uv` so the repo helpers and environment rules are applied consistently.

From the repo root or the `backend` folder, initialize or synchronize the environment with:

```bash
cd backend
uv sync
```

`uv sync` will ensure the `.venv` and project dependencies are in place according to the repository configuration.

After `uv sync`, run commands with `uv run ...` as shown below.


### Run the Flask development server

```bash
cd backend
uv run flask --app app.py run --host 0.0.0.0 --port 5000 --debug
```


### Run tests

```bash
cd backend
uv run python -m pytest 
```

And with coverage:

```bash
cd backend
uv ruv run python -m pytest --cov=backend --cov-report=term-missing -q
```


## Architecture & extension points

High level:

- Models: `models.py` defines the domain objects and DB mappings used by routes and the scheduler.
- Scheduler core: `scheduler.py` constructs BoolVars for candidate assignments and applies restrictions. Each restriction is implemented as a small class in `restrictions/` and exposes an `apply(model, assignments, ...)` method.
- Restrictions: Each file in `restrictions/` contains focused logic and unit tests in `test/restrictions/`. Tests usually create a minimal CpModel and mock Subjects/Teachers where needed.
- APIs: `routes/` contains Flask route modules that serialize SQLAlchemy models into Pydantic schemas in `schemas.py` before returning JSON.

Adding a new restriction (recommended steps):

1. Create a new file `backend/restrictions/<your_restriction>.py` and add a class that subclasses `Restriction` (see `restrictions/base.py`).
2. Implement an `apply(self, model, assignments, **ctx)` method that adds constraints to the OR-Tools model.
3. Add a unit test under `backend/test/restrictions/test_<your_restriction>.py` that constructs a small CpModel and asserts feasibility/infeasibility to exercise your rule.
4. Run the test suite and a short scheduler run via `uv run` to ensure it behaves as expected.

## Database

- Default DB file: `agenda.db` (located at repository root in many setups).
- For development you can delete the DB file and re-run the populate step via `uv` to reset it.

## Docker

The repository includes a `Dockerfile` for the backend. Use the root-level `docker-compose.yml` to run the full stack (frontend + backend + any other services) in an isolated environment.

## Debugging tips

- If the scheduler fails to find a solution, try running with a small dataset (the tests include minimal examples) and inspect the printed model statistics.
- If Flask routes fail serialization, check `schemas.py` — the codebase uses Pydantic v2 for response validation and serialization.

## Where to look next

- `backend/restrictions/` — individual scheduling constraints and tests.
- `backend/scheduler.py` — how assignments are modelled and how restrictions are applied.
- `backend/models.py` — DB shape and relationships used by the scheduler and routes.

If you'd like, I can also:
- Add a `backend/README-DEV.md` with a step-by-step local development checklist tailored to your OS.
- Create a `.env.example` for configurable variables used by Flask and the scheduler.
- Add a small helper script that runs a smoke scheduler job and prints results to console for debugging.

Tell me which follow-up you'd like and I'll add it.
- APIs: `routes/` contains Flask route modules that serialize SQLAlchemy models into Pydantic schemas in `schemas.py` before returning JSON.
