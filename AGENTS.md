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

## Conventions


### Restrictions
For diagnostics, soft and hard constraints, dict filtering, CP-SAT patterns see `.agents/skills/ortools/SKILL.md`.


## Known gotchas

- Hardcoded `range(5)` in some restriction files (`subject_max_hours_per_day.py`, `teacher_one_subject_per_group.py`) — should use `num_days`/`num_hours` parameters
- Group name mismatch: user enters `"1ºA"` but scheduler uses `"1º-A"` — use `normalize_group_name()`
- Subject in multiple SubjectGroups is invalid (conflicting constraints)
- Missing `__init__.py` import OR missing `scheduler.py` wiring → restriction silently not applied
- Compose files mount the repo root as /app; the SQLite DB must be writable at runtime
- `teacher_subject.included_lines` is a JSON array of ints (`null` = all lines). Filter is AND with `Subject.included_lines` — both must allow the line for assignment variables to be created.

## Documentation

- `docs/GUIA_USUARIO.md` (Spanish) and `docs/USER_GUIDE.md` (English) — user-facing guides
- Keep them in sync with the actual UI: update when routes, forms, labels, or UI copy change
- For any change in documentation see `.agents/skills/tech-writer/SKILL.md`

## Detailed references

- `.agents/skills/backend/SKILL.md` — Backend development: Flask app structure, route blueprints, SQLAlchemy models, Pydantic schemas, i18n, logging, task manager, seeding
- `.agents/skills/ortools/SKILL.md` — Restriction development: CP-SAT variable structure, filtering, diagnostics, hard/soft restrictions
- `.agents/skills/frontend/SKILL.md` — Frontend component: tree, CSS design system, i18n, API patterns
- `.agents/skills/tech-writer/SKILL.md` - Documentation and user guides.
