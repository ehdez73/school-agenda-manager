---
name: backend
description: >-
  Architecture and conventions for the Python/Flask backend of the School
  Agenda Manager. Covers Flask setup, route blueprints, SQLAlchemy models,
  Pydantic v2 schemas, DB seeding, i18n, logging, async task management,
  and extension patterns.
---

# Backend Skill — Flask App Architecture & Conventions

Practical guide for working with the Flask backend. Covers the actual
patterns, module structure, and wiring used in this codebase.

---

## 1. Flask App Structure

### 1.1 Entrypoint

`backend/app.py`:

```python
# populate_db runs on every startup — seeds DB if tables are empty
populate_db("backend/init-data.json")

app = Flask(__name__)
CORS(app)

@app.before_request
def set_request_locale():
    locale = request.headers.get("X-Locale") or DEFAULT_LOCALE
    set_locale(locale)

# Register all blueprints
app.register_blueprint(courses_bp)
app.register_blueprint(subjects_bp)
# ... etc
```

### 1.2 Blueprint pattern

Each route module in `backend/routes/` creates a blueprint and registers
routes on it:

```python
from flask import Blueprint, jsonify, request, abort
from ..models import Session
from ..schemas import SomeSchema
from ..translations import t

some_bp = Blueprint('some_bp', __name__)
logger = logging.getLogger(__name__)

@some_bp.route('/some-resource', methods=['GET'])
def list_resources():
    session = Session()
    items = session.query(SomeModel).all()
    session.close()
    return jsonify([SomeSchema(**i.to_dict()).model_dump() for i in items])
```

### 1.3 Blueprint registration order

In `app.py`, all blueprints must be registered. Currently registered:

| Blueprint | Module | Prefix |
|-----------|--------|--------|
| `courses_bp` | `routes/courses.py` | implicit |
| `subjects_bp` | `routes/subjects.py` | implicit |
| `teachers_bp` | `routes/teachers.py` | implicit |
| `subject_groups_bp` | `routes/subject_groups.py` | implicit |
| `export_import_bp` | `routes/export_import.py` | implicit |
| `timetable_bp` | `routes/timetable.py` | /api/timetable* |
| `fixed_slots_bp` | `routes/fixed_slots.py` | implicit |
| `config_bp` | `routes/config.py` | implicit |
| `docs_bp` | `routes/docs.py` | implicit |

---

## 2. Route Patterns

### 2.1 Standard CRUD flow

```python
@some_bp.route('/resource', methods=['GET'])
def list_all():
    session = Session()
    items = session.query(Model).all()
    session.close()
    return jsonify([Schema(**i.to_dict()).model_dump() for i in items])

@some_bp.route('/resource/<id>', methods=['GET'])
def get_one(id):
    session = Session()
    item = session.get(Model, id)
    session.close()
    if item is None:
        abort(404, description=t('errors.not_found', entity='Model', id=id))
    return jsonify(Schema(**item.to_dict()).model_dump())

@some_bp.route('/resource', methods=['POST'])
def create():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description=t('errors.missing_field', field='name'))
    session = Session()
    item = Model(id=data['name'])
    session.add(item)
    session.commit()
    result = Schema(**item.to_dict()).model_dump()
    session.close()
    return jsonify(result), 201

@some_bp.route('/resource/<id>', methods=['DELETE'])
def delete(id):
    session = Session()
    item = session.get(Model, id)
    if item is None:
        session.close()
        abort(404, description=t('errors.not_found', entity='Model', id=id))
    session.delete(item)
    session.commit()
    session.close()
    return jsonify({"message": t('success.deleted', entity='Model', id=id)}), 200
```

### 2.2 Session lifecycle

- `Session` is imported from `models.py` (`from ..models import Session`)
- A new session is created per request — **no `g`-based session** pattern
- Must be closed explicitly: `session.close()`
- Catch-22: if you `abort()` after opening, the session leaks — use `try/finally` or close before abort

### 2.3 Error responses

```python
abort(400, description=t('errors.missing_field', field='name'))
# Returns {"error": "Missing required field 'name'"} with the locale-appropriate message
```

### 2.4 Route with both int and string path params

Some resources accept both types (e.g. course IDs can be `"1º"` or `1`):

```python
@some_bp.route('/resource/<int:item_id>', methods=['GET'])
@some_bp.route('/resource/<string:item_id>', methods=['GET'])
def get_item(item_id):
    ...
```

---

## 3. DB Models & Session

### 3.1 Engine, Base, Session

Defined at module level in `backend/models.py`:

```python
ENGINE = create_engine("sqlite:///agenda.db",
                       connect_args={"check_same_thread": False})
Base = declarative_base()
Session = sessionmaker(bind=ENGINE)

Base.metadata.create_all(ENGINE)  # runs at import time
```

The database file is `agenda.db` at the repo root (relative to CWD when
running `uv run flask --app app.py run` from `backend/`).

### 3.2 Model classes

| Model | Table | Primary Key | Key relationships |
|-------|-------|-------------|-------------------|
| `Course` | `courses` | `id` (str) | one-to-many: `subjects`, `timeslots` |
| `Subject` | `subjects` | `id` (str) | M-to-N: `teachers`, `subject_groups`; FK to `Course`, self-FK `linked_subject_id` |
| `SubjectGroup` | `subject_groups` | `id` (int) | M-to-N: `subjects` via `subjectgroup_subject` |
| `Teacher` | `teachers` | `id` (int) | M-to-N: `subjects` via `teacher_subject`; one-to-many: `busy_slots` |
| `Timeslot` | `timeslots` | `id` (int) | one-to-many: `timeslot_assignments`; FK to `Course`, FK to `SubjectGroup` |
| `TimeSlotAssignment` | `timeslot_assignments` | `id` (int) | FK to `Timeslot`, `Subject`, `Teacher` |
| `FixedSlot` | `fixed_slots` | `id` (int) | — (visual rows for timetable display) |
| `TeacherBusySlot` | `teacher_busy_slots` | `id` (int) | FK to `Teacher` (coordination/meeting slots) |
| `Config` | `config` | `id` (int) | Singleton row: `classes_per_day`, `days_per_week`, `disabled_restrictions` |

### 3.3 Many-to-Many tables

```python
# Teacher ↔ Subject
teacher_subject = Table(
    "teacher_subject", Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.id")),
    Column("subject_id", Integer, ForeignKey("subjects.id")),
)

# SubjectGroup ↔ Subject
subjectgroup_subject = Table(
    "subjectgroup_subject", Base.metadata,
    Column("subjectgroup_id", Integer, ForeignKey("subject_groups.id")),
    Column("subject_id", String(20), ForeignKey("subjects.id")),
)
```

### 3.4 Key model fields

**Subject:**
- `course_id` (FK → Course.id) — which course this subject belongs to
- `weekly_hours` — total hours per week
- `max_hours_per_day` — daily limit for this subject
- `consecutive_hours` (bool) — if True, hours must be consecutive blocks; if False, must NOT be consecutive
- `teach_every_day` (bool) — must be taught at least once every day
- `linked_subject_id` (self-FK) — another subject that must be scheduled consecutively
- `included_lines` (JSON or null) — which lines/groups in the course this subject applies to
- `color` — hex color for UI display

**Teacher:**
- `subjects` (M:N) — which subjects this teacher can teach
- `max_hours_week` — maximum teaching hours
- `coordination_hours` — non-teaching hours (persisted as `TeacherBusySlot` post-solve)
- `preferences` (JSON) — dict of day → {unavailable: [...], preferred: [...]}
- `tutor_group` (JSON array or string) — which groups this teacher is tutor of

**SubjectGroup:**
- `subjects` (M:N) — subjects that share a timeslot
- `shared_hours` (int or null) — number of hours shared among all members
- `included_lines` (JSON or null) — which lines/groups this group applies to

**Config:**
- `classes_per_day` — number of teaching hours per day
- `days_per_week` — number of teaching days
- `hour_names` — optional display names for each hour slot
- `day_indices` — optional custom day indices
- `disabled_restrictions` — JSON array of restriction names to skip

### 3.5 The `to_dict()` convention

Every model has a `to_dict()` method that returns a plain dict suitable
for Pydantic schema construction. This is the standard serialization
path:

```python
jsonify(SomeSchema(**model.to_dict()).model_dump())
```

### 3.6 No migrations

There is no Alembic or migration system. Schema changes require deleting
`agenda.db` and letting `Base.metadata.create_all(ENGINE)` recreate it.
Seed data is re-applied by `populate_db()` on startup.

---

## 4. Pydantic v2 Schemas

### 4.1 Schema location

All schemas in `backend/schemas.py`.

### 4.2 Standard schema pattern

```python
from pydantic import BaseModel
from typing import Optional, List

class SomeSchema(BaseModel):
    id: str
    name: str
    some_field: Optional[int] = None
    items: List[dict] = []
```

### 4.3 Input validation schemas

```python
from pydantic import BaseModel, Field

class CreateSchema(BaseModel):
    slot_type: str = Field(..., pattern="^(course|teacher)$")
    position: int = Field(..., ge=1)
    label: str = Field(..., min_length=1)
```

### 4.4 RootModel for dynamic keys

```python
class PreferencesSchema(RootModel[Dict[Union[int, str], DayPreferences]]):
    root: Dict[Union[int, str], DayPreferences] = Field(default_factory=dict)
```

### 4.5 Serialization usage

```python
# Response serialization (model → schema → dict → JSON)
CourseSchema(**course.to_dict()).model_dump()

# Input validation (JSON request body → schema)
data = CreateSchema(**request.get_json())
```

---

## 5. Database Seeding

### 5.1 Startup flow

`app.py` calls `populate_db("backend/init-data.json")` on every startup.
This checks if essential tables are empty before inserting seed data.

### 5.2 Seed data

`backend/init-data.json` contains the full seed payload with courses,
subjects, teachers, subject groups, config, and fixed slots. The format
is a JSON object with arrays for each entity type.

### 5.3 Resetting the database

```bash
rm ../agenda.db   # from backend/
uv run flask --app app.py run   # recreates DB and seed data on startup
```

Or from repo root:

```bash
rm agenda.db
cd backend && uv run flask --app app.py run
```

---

## 6. i18n

### 6.1 Translation function

```python
from ..translations import t

# Simple key lookup
t('errors.not_found', entity='Course', id=course_id)
# → "Course with ID 1 not found" or the Spanish equivalent
```

### 6.2 Locale resolution

1. Check `X-Locale` request header
2. Fall back to `DEFAULT_LOCALE = "es"` (defined in `backend/constants.py`)
3. Set per-request in `@app.before_request` via `set_locale(locale)`

### 6.3 Translation dictionary

Defined in `backend/translations.py` as `_LOCALES["en"]` and
`_LOCALES["es"]` dicts. Template variables use `{varname}` syntax.

### 6.4 Adding a new key

Add the string to both `_LOCALES["en"]` and `_LOCALES["es"]` in
`translations.py`, then use via `t('namespace.key', **vars)`.

---

## 7. Logging

### 7.1 Setup

```python
from ..logging_config import setup_logging, build_log_extra, get_request_id

setup_logging()  # called once at the top of app.py
```

The formatter includes `request_id` and `task_id` in every log line:

```
%(asctime)s %(levelname)s [%(name)s] request_id=%(request_id)s task_id=%(task_id)s %(message)s
```

### 7.2 Contextual logging

```python
logger.info("Course created", extra=build_log_extra(task_id=task_id))
# When called within a request: request_id is auto-populated
# task_id is optional, defaults to "-"
```

### 7.3 Log level

Controlled by `BACKEND_LOG_LEVEL` environment variable (default: `INFO`).

---

## 8. Async Task Management

### 8.1 TaskManager

`backend/task_manager.py` provides an in-memory, thread-safe singleton:

```python
from ..task_manager import task_manager

task_id = task_manager.create_task()       # returns UUID string
task_manager.update_progress(task_id, "phase2", details_str)
task_manager.complete_task(task_id)
task_manager.fail_task(task_id, error="...", details="...")
task_manager.cancel_task(task_id)
```

### 8.2 Background solver pattern

```python
thread = threading.Thread(target=_run_solver_in_background, args=(task_id,), daemon=True)
thread.start()
```

The background thread creates its own DB session, calls `create_timetable(session, ...)`, and updates `task_manager` with progress/result.

### 8.3 Polling API

The frontend polls the task status via:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/timetable` | POST | Start generation (returns task_id, 202) |
| `/api/timetable/status/<task_id>` | GET | Poll task status |
| `/api/timetable/status/current` | GET | Get current/latest task status |
| `/api/timetable/<task_id>/cancel` | POST | Request cancellation |
| `/api/timetable` | GET | Get last generated timetable markdown |
| `/api/timetable` | DELETE | Clear current timetable |

### 8.4 Task status lifecycle

`pending` → `running` → `success` | `error` | `cancelled`

---

## 9. Extension Checklist

### 9.1 Add a new DB model

1. Add class in `backend/models.py` with `__tablename__`, columns, `to_dict()`
2. Add any join tables if needed
3. `Base.metadata.create_all(ENGINE)` at bottom of file picks it up automatically
4. Seed data: add entries to `backend/init-data.json`

### 9.2 Add a new API endpoint

1. Create `backend/routes/your_resource.py` with a blueprint
2. Add Pydantic schemas in `backend/schemas.py` if needed
3. Register blueprint in `app.py`
4. Write test in `backend/test/` following existing patterns

### 9.3 Add a new restriction

**This requires three steps — forgetting either will silently skip the restriction:**

1. Create file in `backend/restrictions/` subclassing `Restriction`
2. Import and add to `__all__` in `backend/restrictions/__init__.py`
3. Wire into `scheduler.py`: add tuple to `_build_hard_restrictions()` or `_build_soft_restrictions()`

See `.agents/skills/ortools/SKILL.md` for the full restriction implementation guide.

### 9.4 Add a new translation key

1. Add to both `_LOCALES["en"]` and `_LOCALES["es"]` dicts in `backend/translations.py`
2. Use via `t('namespace.key', **vars)` in routes

### 9.5 Verify changes

```bash
cd backend
uv run python -m pytest -q                                          # all tests
uv run python -m pytest --cov=backend --cov-report=term-missing -q  # with coverage
```
