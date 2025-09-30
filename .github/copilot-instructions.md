# Project Overview

This project is a web application that allows users to generate a schedule for all courses at a school. It is built using React and Python, and uses SQLite for data storage.

A weekly timetable must be generated for all subjects and grades, taking into account the weekly hours of each subject and that a teacher cannot teach two classes at the same time.


## Big picture
- Frontend: `frontend/` — React + Vite UI. Keep changes here isolated to UI-only tasks.
- Backend: `backend/` — Python + Flask app, SQLite DB (`agenda.db`), and the CP-SAT scheduler (OR-Tools). The scheduler models constraints and produces Activities/Timeslots saved to the DB.
- Core scheduling logic lives in `backend/restrictions/` (each Restriction is a class) and `backend/scheduler.py` which wires the OR-Tools model.

Key files to read first:
- `backend/models.py` — ORM / domain models used across backend (Course, Subject, Teacher, Activity, Timeslot).
- `backend/restrictions/*.py` — individual constraint implementations (each exposes an `apply(model, assignments, ...)` method).
- `backend/scheduler.py` — builds variables, applies restrictions, runs CP-SAT solver and saves results.
- `backend/populate_db.py` — helper to seed the SQLite DB for local testing.


# Project Overview

This project is a web application that allows users to generate a schedule for all courses at a school. It is built using React and Python, and uses SQLite for data storage.

A weekly timetable (Monday to Friday) must be generated for all subjects and grades, taking into account the weekly hours of each subject and that a teacher cannot teach two classes at the same time.


## Project-specific conventions
- Restriction classes: placed in `backend/restrictions/` and subclass `Restriction` (see `backend/restrictions/base.py`). Each implements apply(model, assignments, ...) and expects `assignments` to be a dict keyed like `(group, subject_id, teacher_id, day, hour)` mapped to BoolVars.
- Tests: use `pytest` and the OR-Tools `CpModel` helpers. Test files that assert feasibility/infeasibility live near the restriction implementations under `backend/restrictions/test_*.py`.
- Virtualenv: project Python environment is kept at `backend/.venv` (use that interpreter for running tests and scripts).
- follow the styling guide in `frontend/STYLING_GUIDE.md` for frontend CSS.
- The timetable is rendered using markdown in `backend/timetable.py` and displayed in the frontend with `react-markdown` in `frontend/src/components/MarkdownTimetable.tsx`.

## Common tasks / commands (zsh/macOS)

IMPORTANT: To run the backend you need to be placed in the `backend/` directory.
When using GitHub Copilot to execute  uv commands, prefix them with `cd backend &&` to ensure the correct directory.


```zsh
cd backend
uv sync
uv run flask --app app.py run --host 0.0.0.0 --port 5000 --debug
```

To run the tests:

```zsh
cd backend
uv run python -m pytest
```

## Integration notes & gotchas
- OR-Tools CP-SAT is used heavily; models use BoolVars aggregated with sum(...) to create linear constraints. Pay attention to generator expressions — some code uses model.AddAtMostOne(...) or model.Add(sum(vars) <= k).
- Assignments dict keys are the single source-of-truth for indexing decisions; keep that shape when adding tests or new restrictions.
- Tests frequently create minimal MockSubject/MockTeacher classes — follow those small patterns when writing unit tests.
- SQLite Database file `agenda.db` is in the repo root. CI or contributor runs might overwrite it; run `populate_db.py` to recreate expected schema/data.

## How to extend
- To add a new restriction: add a new file in `backend/restrictions/`, implement `apply(...)`, add a small unit test under `backend/restrictions/test_<name>.py` that constructs a minimal CpModel to exercise the constraint.
- After changes, run the related tests and a quick scheduler run to ensure the model still solves.

If anything above is unclear or you'd like instructions tuned to a specific task (add restriction, debug solver, extend frontend), tell me which area and I'll expand this file.

## Pydantic usage
- The backend now uses Pydantic (v2) models for response serialization and simple validation.
- Schemas live in `backend/schemas.py`. Routes construct small dicts from SQLAlchemy models and pass them to the Pydantic schemas before returning JSON. When editing route responses, prefer updating or reusing those schemas.
