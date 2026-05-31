# AGENTS.md — School Agenda Manager

## Repo layout

- `backend/` — Python 3.13 Flask app, SQLAlchemy ORM, OR-Tools CP-SAT scheduler
- `frontend/` — React 19 + Vite 7 SPA (JSX, no TypeScript, no React Router, no Context, no CSS-in-JS/Tailwind)

## Commands

All backend commands **must** run from the `backend/` directory via `uv run`:

```bash
cd backend
uv sync                           # install deps (uv.lock-managed)
uv run flask --app app.py run --host 0.0.0.0 --port 5000 --debug
uv run python -m pytest           # run all backend tests
uv run python -m pytest --cov=backend --cov-report=term-missing -q  # coverage
uv run python -m pytest test/restrictions/test_teacher_one_class_at_a_time.py  # single file
uv run python -m pytest -k "test_my_rule"  # single test name
```

Frontend commands from `frontend/`:

```bash
npm install
npm run dev                       # vite dev (proxy: /api -> localhost:5000)
npm test                          # vitest run
npm run test:coverage             # vitest run --coverage
npm run lint                      # eslint (flat config)
```

Docker (from repo root):

```bash
docker compose up --build
```

## Key files & entrypoints

- `backend/app.py` — Flask init, blueprint registration, runs `populate_db` on startup
- `backend/models.py` — SQLAlchemy models: Course, Subject, Teacher, Timeslot, SubjectGroup, FixedSlot, TeacherBusySlot, Config
- `backend/scheduler.py` — builds CP-SAT model, applies restrictions, saves solution to DB
- `backend/scheduler.py:create_timetable()` — main entry point for timetable generation
- `backend/restrictions/base.py` — Restriction ABC (implement `apply(model, assignments, ...)`)
- `backend/restrictions/__init__.py` — **must** import new restrictions here AND wire in `scheduler.py`
- `backend/schemas.py` — Pydantic v2 response schemas
- `backend/translations.py` — custom i18n helper, default locale `"es"`
- `backend/constants.py` — `DEFAULT_LOCALE = "es"`
- `frontend/src/App.jsx` — root component, `useState`-based page routing (no React Router)
- `frontend/src/index.css` — CSS entry, imports layers in order: `globals.css > utilities.css > components.css` then component CSS
- `frontend/src/lib/api.js` — native `fetch` wrapper
- `frontend/src/i18n/index.js` — custom i18n helper

## Architecture notes

- **Decision variables**: `assignments[(group, subject_id, teacher_id, day, hour)]` = `BoolVar`
  - Only valid (group belongs to course, teacher can teach subject) combos are created in `_create_assignments()`
- **Group format**: `"{course.id}-{line_char}"` e.g. `"1º-A"`, `"2-B"`
  - Use `normalize_group_name()` from `tutor_mandatory_hours.py` to parse user input: `"1ºA"` → `"1º-A"`
- **Hard restrictions**: listed in `_build_hard_restrictions()`, always enforced
- **Soft restrictions**: listed in `_build_soft_restrictions()`, use `preference_terms` list; `model.Maximize(sum(preference_terms))`
- **Infeasibility diagnosis**: 3-phase (sanity checks → isolation → entity-level), results as markdown string
- **Vite proxy**: `/api/*` in dev rewrites to `http://localhost:5000/*` (no `/api` prefix on backend)
  - Production uses `VITE_API_BASE` env var (default: `/api`)
- **SQLite DB**: `agenda.db` at repo root. Delete and re-run backend to regenerate seed data.

## Conventions

### Restrictions (backend)
1. Create file in `backend/restrictions/`
2. Subclass `Restriction`, implement `apply(self, model, assignments, ...)`
3. Import in `restrictions/__init__.py` and add to `__all__`
4. Wire in `scheduler.py` (`_build_hard_restrictions()` or `_build_soft_restrictions()`)
5. Write test in `backend/test/restrictions/test_<name>.py` with local Mock classes
6. For diagnostic support: override `apply_with_assumptions()` returning `[(BoolVar, entity_info_dict)]`
7. Soft constraints: store `self.preference_terms`, accept `weight` param in `__init__`

### Restrictions — dict filtering
See `.agents/skills/ortools/SKILL.md` §3.

### Frontend
See `.agents/skills/frontend/SKILL.md`.

## Testing gotchas

- Backend tests: `conftest.py` adds `backend/` to sys.path so imports work
- Restriction tests use local MockTeacher, MockSubject, MockSubjectGroup classes (no DB needed)
- Feasibility test: assert `status in (cp_model.OPTIMAL, cp_model.FEASIBLE)`
- Infeasibility test: force conflicting assignments with `model.Add(var == 1)` then assert `status == cp_model.INFEASIBLE`
- Solution verification: read with `solver.Value(assignments[key])` and check invariants
- Frontend tests: in `frontend/src/components/__tests__/`, Vitest with jsdom environment

## Known gotchas

- Hardcoded `range(5)` in some restriction files (`subject_max_hours_per_day.py`, `teacher_one_subject_per_group.py`) — should use `num_days`/`num_hours` parameters
- Group name mismatch: user enters `"1ºA"` but scheduler uses `"1º-A"` — use `normalize_group_name()`
- Subject in multiple SubjectGroups is invalid (conflicting constraints)
- Missing `__init__.py` import OR missing `scheduler.py` wiring → restriction silently not applied
- Compose files mount the repo root as /app; the SQLite DB must be writable at runtime

## Documentation

- `docs/GUIA_USUARIO.md` (Spanish) and `docs/USER_GUIDE.md` (English) — user-facing guides
- Keep them in sync with the actual UI: update when routes, forms, labels, or UI copy change

## Detailed references

- `.agents/skills/backend/SKILL.md` — Flask app structure, route blueprints, SQLAlchemy models, Pydantic schemas, i18n, logging, task manager, seeding
- `.agents/skills/ortools/SKILL.md` — CP-SAT variable structure, filtering, diagnostics, testing
- `.agents/skills/frontend/SKILL.md` — component tree, CSS design system, i18n, API patterns
