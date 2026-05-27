---
name: ortools
description: >-
  Expert guidance on adding new restrictions to the school timetable scheduler
  using Google OR-Tools CP-SAT. Covers the actual decision variable structure,
  the Restriction base-class pattern, dict-filtering conventions, diagnostic
  support, soft constraint patterns, and testing strategies used in this project.
---

# OR-Tools Skill — Adding Constraints to the School Timetable

Practical guide for adding new restrictions to the scheduling solver using
Google OR-Tools CP-SAT. Covers the actual patterns used in this codebase.

---

## 0. How the Scheduler Works

### 0.1 Decision Variables

Every possible (teacher, subject, group, day, hour) combination is a single
`BoolVar` (0 or 1):

```python
key = (group, subject_id, teacher_id, day, hour)
assignments[key] = model.NewBoolVar(f"g:{group} sub:{sid} t:{tname} d:{d} h:{h}")
```

`assignments[key] == 1` means "this teacher teaches this subject to this group
at this day+hour slot." Only valid combinations (group belongs to course,
teacher can teach that subject) are created by `_create_assignments()`.

### 0.2 The Restriction Base Class

`backend/restrictions/base.py`:

```python
class Restriction(ABC):
    @abstractmethod
    def apply(self, model, assignments, *args, **kwargs):
        """Add constraints to the CP-SAT model."""
        ...

    def apply_with_assumptions(self, model, assignments, *args, **kwargs):
        """Same as apply but returns (BoolVar, entity_info) pairs for diagnostics.

        Default implementation calls apply() and returns [].
        Override to support SufficientAssumptionsForInfeasibility().
        """
        self.apply(model, assignments, *args, **kwargs)
        return []

    @property
    def name(self):
        return self.__class__.__name__
```

### 0.3 How Restrictions Are Applied

In `scheduler.py`, two paths:

**Hard constraints** — listed in `_build_hard_restrictions()`:
```python
def _build_hard_restrictions(...):
    return [
        ("SubjectWeeklyHours", SubjectWeeklyHours(), [model, assignments, all_groups, all_subjects]),
        ("TeacherOneClassAtATime", TeacherOneClassAtATime(), [model, assignments, all_teachers, num_days, num_hours]),
        # ... add yours here
    ]

for name, restriction, args in hard_restrictions:
    if name not in skip_restrictions:
        restriction.apply(*args)
```

**Soft constraints** — applied in `solve_scheduling_model()`, collect
`preference_terms` for the objective:
```python
teacher_preferred = TeacherPreferredTimes()
teacher_preferred.apply(model, assignments, all_teachers, num_days, num_hours)
tutor_pref = TutorPreference(weight=100)
tutor_pref.apply(model, assignments, all_teachers)

preference_terms = teacher_preferred.preference_terms + tutor_pref.preference_terms
if preference_terms:
    model.Maximize(sum(preference_terms))
```

---

## 1. Quick Start — Add a New Restriction in 5 Steps

### Step 1: Create the restriction file

`backend/restrictions/your_rule_name.py`:

```python
from .base import Restriction


class YourRuleName(Restriction):
    """Description of what this restriction enforces."""

    def apply(self, model, assignments, groups, num_days, num_hours):
        for group in groups:
            for d in range(num_days):
                for h in range(num_hours):
                    slot_vars = [
                        assignments[k]
                        for k in assignments
                        if k[0] == group and k[3] == d and k[4] == h
                    ]
                    model.AddAtMostOne(slot_vars)
```

### Step 2: Register in `restrictions/__init__.py`

```python
from .your_rule_name import YourRuleName

__all__ = [
    # ... keep existing entries ...
    "YourRuleName",
]
```

### Step 3: Wire into `scheduler.py`

**Hard constraint** — add a tuple to `_build_hard_restrictions()`:
```python
("YourRuleName", YourRuleName(), [model, assignments, ...]),
```

**Soft constraint** — apply separately in `solve_scheduling_model()`:
```python
my_rule = YourRuleName(weight=50)
my_rule.apply(model, assignments, ...)
preference_terms += my_rule.preference_terms
```

### Step 4: Add diagnostic support (optional)

Override `apply_with_assumptions` to enable entity-level infeasibility diagnosis:

```python
def apply(self, model, assignments, teachers):
    self._apply_impl(model, assignments, teachers)

def apply_with_assumptions(self, model, assignments, teachers):
    return self._apply_impl(model, assignments, teachers, diagnostic_mode=True)

def _apply_impl(self, model, assignments, teachers, diagnostic_mode=False):
    assumptions = []
    for teacher in teachers:
        total = sum(assignments[k] for k in assignments if k[2] == teacher.id)
        if diagnostic_mode:
            assume = model.NewBoolVar(f"assume_rule_{teacher.id}")
            model.Add(total <= teacher.max_hours_week).OnlyEnforceIf(assume)
            assumptions.append((assume, {
                "restriction": "YourRuleName",
                "entity_type": "teacher",
                "entity_id": teacher.id,
                "entity_name": teacher.name,
            }))
        else:
            model.Add(total <= teacher.max_hours_week)
    return assumptions
```

### Step 5: Write tests

```python
from ortools.sat.python import cp_model
from backend.restrictions.your_rule_name import YourRuleName


class MockTeacher:
    def __init__(self, id, name="Test", max_hours_week=20):
        self.id = id
        self.name = name
        self.max_hours_week = max_hours_week


def test_your_rule_works():
    model = cp_model.CpModel()
    teachers = [MockTeacher("t1")]
    assignments = {
        ("1-A", "s1", "t1", 0, 0): model.NewBoolVar("a"),
    }
    YourRuleName().apply(model, assignments, teachers)
    status = cp_model.CpSolver().Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
```

---

## 2. CP-SAT API Quick Reference

### Variables
| API | Purpose |
|-----|---------|
| `model.NewBoolVar(name)` | 0 or 1 — this is what all assignments are |
| `model.NewIntVar(lb, ub, name)` | Integer in [lb..ub] |

### Constraints
| API | Use |
|-----|-----|
| `model.Add(expr)` | Any linear expression: `sum(vars)`, `x + y`, `5*x + 3*y` |
| `model.AddAtMostOne(vars)` | At most one var is 1 |
| `model.AddExactlyOne(vars)` | Exactly one var is 1 |
| `model.AddBoolOr(lits)` | At least one literal true |
| `model.AddBoolAnd(lits)` | All literals true |
| `model.AddImplication(a, b)` | If a==1 then b==1 |

### Conditional Constraints
```python
model.Add(y >= 10).OnlyEnforceIf(x)         # if x==1 then y >= 10
model.Add(y >= 10).OnlyEnforceIf([x, z])    # if x==1 AND z==1 then y >= 10
model.Add(y >= 10).OnlyEnforceIf(x.Not())   # if x==0 then y >= 10  (negation)
```

### Element Constraint (variable as index)
```python
model.AddElement(index_var, array, result_var)  # result_var == array[index_var]
```

### Objective
```python
model.Maximize(sum(weighted_terms))
model.Minimize(sum(weighted_terms))
```

### Solving
```python
solver = cp_model.CpSolver()

solver.parameters.max_time_in_seconds = 60.0   # 60s timeout
solver.parameters.num_search_workers = 8       # parallel threads (optional)
solver.parameters.log_search_progress = True   # verbose output for debugging

status = solver.Solve(model)

if status == cp_model.OPTIMAL:       # proven optimal
elif status == cp_model.FEASIBLE:    # solution found (optimality not proven)
elif status == cp_model.INFEASIBLE:  # no solution possible
elif status == cp_model.MODEL_INVALID:  # model definition error

solver.Value(x)        # read BoolVar or IntVar value
solver.ObjectiveValue()
```

---

## 3. The Dict-Filtering Pattern

This project does NOT use a separate index class. Restrictions filter the flat
`assignments` dict with list comprehensions. This is O(N) per filter but the
set of assignments is small enough.

Tuple key components: `(group, subject_id, teacher_id, day, hour)`

| Index | Expression |
|-------|------------|
| By teacher | `k[2] == teacher.id` |
| By subject | `k[1] == subject.id` |
| By group | `k[0] == group` |
| By day | `k[3] == d` |
| By hour | `k[4] == h` |

### Common filter patterns

```python
# Teacher at a specific day+hour
vars = [assignments[k] for k in assignments
        if k[2] == teacher.id and k[3] == d and k[4] == h]

# Group+subject (all teachers, all slots)
vars = [assignments[k] for k in assignments
        if k[0] == group and k[1] == subject.id]

# Group+subject+day (all hours)
vars = [assignments[k] for k in assignments
        if k[0] == group and k[1] == subject.id and k[3] == d]

# Group+subject+day+hour (all teachers at one slot)
vars = [assignments[k] for k in assignments
        if k[0] == group and k[1] == subject.id and k[3] == d and k[4] == h]

# Teacher total load (all groups, subjects, days, hours)
total = sum(assignments[k] for k in assignments if k[2] == teacher.id)

# Group slot (one-subject-per-group check)
slot_vars = [assignments[k] for k in assignments
             if k[0] == group and k[3] == d and k[4] == h]
```

---

## 4. Common Restriction Patterns

### 4.1 At-Most-One (Mutual Exclusion)

```python
# TeacherOneClassAtATime: teacher can't be in two groups at once
for teacher in teachers:
    for d in range(num_days):
        for h in range(num_hours):
            model.AddAtMostOne(
                assignments[k] for k in assignments
                if k[2] == teacher.id and k[3] == d and k[4] == h
            )
```

### 4.2 Sum Equality (Exact Count)

```python
# SubjectWeeklyHours: each subject must be taught exactly N hours/week
hours = sum(assignments[k] for k in assignments
            if k[0] == group and k[1] == subject.id)
model.Add(hours == subject.weekly_hours)
```

### 4.3 Sum Inequality (Upper/Lower Bound)

```python
# TeacherMaxWeeklyHours
total = sum(assignments[k] for k in assignments if k[2] == teacher.id)
model.Add(total <= teacher.max_hours_week)

# SubjectMustEveryDay — at least 1 per day
model.Add(sum(vars_for_day) >= 1)

# GroupSubjectMaxHoursPerDay
model.Add(sum(hour_vars) <= subject.max_hours_per_day)
```

### 4.4 Forced Zero (Blocked)

```python
# TeacherUnavailableTimes
model.Add(sum(vars_for_slot) == 0)
```

### 4.5 Aggregation with Auxiliary BoolVars

When multiple teachers can teach the same subject, you need one BoolVar per
slot that indicates "this subject is active at this slot" regardless of which
teacher is assigned. Required for consecutive-hours, linked-subjects, and gap
constraints.

```python
y_vars = []
for h in range(num_hours):
    y = model.NewBoolVar(f"y_{group}_{subject.id}_d{d}_h{h}")
    assign_vars = [
        assignments[k] for k in assignments
        if k[0] == group and k[1] == subject.id and k[3] == d and k[4] == h
    ]
    if assign_vars:
        model.Add(sum(assign_vars) == y)
    else:
        model.Add(y == 0)
    y_vars.append(y)
```

This pattern is used in:
- `GroupSubjectHoursMustBeConsecutive`
- `GroupSubjectHoursMustNotBeConsecutive`
- `LinkedSubjectsConsecutive`

### 4.6 Consecutive Hours (Single Block)

```python
# At most one block-start per day = single contiguous block
starts = []
for h in range(num_hours):
    s = model.NewBoolVar(f"start_{group}_{subject.id}_d{d}_h{h}")
    if h == 0:
        model.Add(s == y_vars[0])
    else:
        model.Add(s >= y_vars[h] - y_vars[h-1])
        model.Add(s <= y_vars[h])
        model.Add(s <= 1 - y_vars[h-1])
    starts.append(s)
model.Add(sum(starts) <= 1)
```

### 4.7 Non-Consecutive Hours

```python
# Adjacent hours cannot both be scheduled
for h in range(num_hours - 1):
    model.Add(y_h + y_h1 <= 1)
```

### 4.8 Logical Unit Grouping

When a SubjectGroup (e.g., Religion + Ethics) shares a slot, the whole group
counts as one "logical unit." At most one logical unit per group/day/hour.

```python
logical_vars = []
for unit_id, unit_keys in logical_units.items():
    unit_vars = [assignments[k] for k in unit_keys]
    if len(unit_vars) == 1:
        logical_vars.append(unit_vars[0])
    else:
        unit_var = model.NewBoolVar(f"logical_{unit_id}")
        model.Add(unit_var <= sum(unit_vars))
        model.Add(sum(unit_vars) <= len(unit_vars) * unit_var)
        logical_vars.append(unit_var)
model.Add(sum(logical_vars) <= 1)
```

### 4.9 SubjectGroup Co-Assignment

Subjects in the same SubjectGroup must be assigned to the same slot:

```python
model.Add(sum(subj1_vars) == sum(subj2_vars))
```

### 4.10 Conditional (Reified)

```python
# Only enforce a constraint when a condition variable is true
pref_var = model.NewBoolVar(f"pref_{teacher.id}")
model.Add(assignments[key] == 1).OnlyEnforceIf(pref_var)
# Include pref_var in the objective with a weight
```

---

## 5. Soft Constraints (Preferences)

| Aspect | Hard | Soft |
|--------|------|------|
| API | `model.Add(...)` | `model.Maximize(sum(weighted_terms))` |
| Guarantee | Must be satisfied | Best-effort |
| Infeasibility risk | Yes | No |

### Soft constraint pattern

```python
class MySoftRule(Restriction):
    def __init__(self, weight: int = 1):
        self.weight = weight
        self.preference_terms = []

    def apply(self, model, assignments, ...):
        self.preference_terms = []
        for ...:
            expr = sum(rewarded_vars)
            if self.weight != 1:
                self.preference_terms.append(self.weight * expr)
            else:
                self.preference_terms.append(expr)
```

In `scheduler.py`:
```python
my_rule = MySoftRule(weight=50)
my_rule.apply(model, assignments, ...)
preference_terms += my_rule.preference_terms
if preference_terms:
    model.Maximize(sum(preference_terms))
```

---

## 6. Diagnostic Support (apply_with_assumptions)

The three-phase diagnostics in `scheduler.py:_run_entity_diagnosis` uses
`SufficientAssumptionsForInfeasibility()` to identify which entities cause
conflicts. A restriction enables this by gating its constraints behind
assumption BoolVars.

### Implementation pattern

```python
def apply(self, model, assignments, teachers):
    self._apply_impl(model, assignments, teachers)

def apply_with_assumptions(self, model, assignments, teachers):
    return self._apply_impl(model, assignments, teachers, diagnostic_mode=True)

def _apply_impl(self, model, assignments, teachers, diagnostic_mode=False):
    assumptions = []
    for teacher in teachers:
        constraint = sum(assignments[k] for k in assignments if k[2] == teacher.id) <= teacher.max_hours_week
        if diagnostic_mode:
            assume = model.NewBoolVar(f"assume_rule_{teacher.id}")
            model.Add(constraint).OnlyEnforceIf(assume)
            assumptions.append((assume, {
                "restriction": "MyRestriction",
                "entity_type": "teacher",
                "entity_id": teacher.id,
                "entity_name": teacher.name,
                "extra": {"max_hours_week": teacher.max_hours_week},
            }))
        else:
            model.Add(constraint)
    return assumptions
```

### Entity info dict

| Key | Required | Description |
|-----|----------|-------------|
| `restriction` | Yes | Class name — must match the key in `_build_hard_restrictions()` |
| `entity_type` | Yes | `"teacher"`, `"subject"`, or `"group"` |
| `entity_id` | Yes | Unique identifier |
| `entity_name` | Yes | Human-readable name |
| `extra` | No | Dict with additional context (shown in diagnostic output) |

### Restrictions that implement this today

- `SubjectWeeklyHours`
- `TeacherMaxWeeklyHours`
- `TeacherUnavailableTimes`
- `TutorMandatoryHours`

---

## 7. Helper: normalize_group_name

Defined in `tutor_mandatory_hours.py` and `tutor_preference.py`. Used whenever
you need to match user-provided group names against the scheduler's format.

```python
def normalize_group_name(group: str) -> str:
    if not group or "-" in group:
        return group
    if len(group) > 1:
        return f"{group[:-1]}-{group[-1]}"
    return group
```

Examples: `"1ºA"` → `"1º-A"`, `"1º-A"` → `"1º-A"` (no-op).

---

## 8. Testing Guide

### Test setup

Each test file defines its own mock classes locally:

```python
from ortools.sat.python import cp_model
from backend.restrictions.my_rule import MyRule


class MockTeacher:
    def __init__(self, id, name="Test", max_hours_week=20, subjects=None,
                 preferences=None, tutor_group=None):
        self.id = id
        self.name = name
        self.max_hours_week = max_hours_week
        self.subjects = subjects or []
        self.preferences = preferences
        self.tutor_group = tutor_group


class MockSubject:
    def __init__(self, id, course_id, weekly_hours=1, max_hours_per_day=1,
                 consecutive_hours=True, teach_every_day=False,
                 linked_subject_id=None):
        self.id = id
        self.course_id = course_id
        self.weekly_hours = weekly_hours
        self.max_hours_per_day = max_hours_per_day
        self.consecutive_hours = consecutive_hours
        self.teach_every_day = teach_every_day
        self.linked_subject_id = linked_subject_id


class MockSubjectGroup:
    def __init__(self, subjects=None, subject_ids=None, name=None):
        self.subjects = subjects or []
        self.subject_ids = subject_ids or []
        self.name = name or str(id(self.subjects))
```

### Test patterns

**Feasibility** — model should be solvable with valid data:
```python
def test_my_rule_allows_valid():
    model = cp_model.CpModel()
    assignments = {("1-A", "s1", "t1", 0, 0): model.NewBoolVar("a")}
    MyRule().apply(model, assignments, ...)
    status = cp_model.CpSolver().Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
```

**Infeasibility** — model should be impossible with conflicting constraints:
```python
def test_my_rule_blocks_invalid():
    model = cp_model.CpModel()
    a = model.NewBoolVar("a")
    assignments = {("1-A", "s1", "t1", 0, 0): a}
    model.Add(a == 1)  # force assignment
    model.Add(a == 0)  # conflict
    MyRule().apply(model, assignments, ...)
    status = cp_model.CpSolver().Solve(model)
    assert status == cp_model.INFEASIBLE
```

**Solution verification** — check invariants post-solve:
```python
def test_my_rule_solution_correct():
    model = cp_model.CpModel()
    # ... build model, apply rule, solve ...
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    for teacher in teachers:
        assigned = sum(
            solver.Value(assignments[k])
            for k in assignments if k[2] == teacher.id
        )
        assert assigned <= teacher.max_hours_week
```

---

## 9. Existing Restrictions Reference

| File | Class | Type | In scheduler? |
|------|-------|------|---------------|
| `subject_weekly_hours.py` | `SubjectWeeklyHours` | Hard | Yes |
| `teacher_one_class_at_a_time.py` | `TeacherOneClassAtATime` | Hard | Yes |
| `teacher_max_weekly_hours.py` | `TeacherMaxWeeklyHours` | Hard | Yes |
| `teacher_unavailable_times.py` | `TeacherUnavailableTimes` | Hard | Yes |
| `group_subject_max_hours_per_day.py` | `GroupSubjectMaxHoursPerDay` | Hard | Yes |
| `group_at_most_one_logical_assignment.py` | `GroupAtMostOneLogicalAssignment` | Hard | Yes |
| `group_subject_hours_must_be_consecutive.py` | `GroupSubjectHoursMustBeConsecutive` | Hard | Yes |
| `group_subject_hours_must_not_be_consecutive.py` | `GroupSubjectHoursMustNotBeConsecutive` | Hard | Yes |
| `linked_subjects_consecutive.py` | `LinkedSubjectsConsecutive` | Hard | Yes |
| `subjectgroup_assignment.py` | `SubjectGroupAssignment` | Hard | Yes |
| `subject_must_every_day.py` | `SubjectMustEveryDay` | Hard | Yes |
| `tutor_mandatory_hours.py` | `TutorMandatoryHours` | Hard | Yes |
| `teacher_preferred_times.py` | `TeacherPreferredTimes` | Soft | Yes |
| `tutor_preference.py` | `TutorPreference` | Soft | Yes |
| `group_at_most_one_subject_per_hour.py` | `GroupAtMostOneSubjectPerHour` | Hard | No — superseded by `GroupAtMostOneLogicalAssignment` |
| `subject_max_hours_per_day.py` | `SubjectMaxHoursPerDay` | Hard | No — uses `GroupSubjectMaxHoursPerDay` instead; file has hardcoded `range(5)` |
| `teacher_one_subject_per_group.py` | `TeacherOneSubjectPerGroup` | Hard | No — has hardcoded `range(5)`, needs refactoring |

---

## 10. OR-Tools Pitfalls (This Project)

| Pitfall | Fix |
|---------|-----|
| Over-constraining → `INFEASIBLE` | Check `num_days × num_hours ≥ total_weekly_hours` |
| Accessing `solver.Value(x)` when `INFEASIBLE` | Always check solver status first |
| `if x:` on a CP-SAT variable (doesn't work) | Use `OnlyEnforceIf(x)` |
| Passing floats to `NewIntVar` | Scale to integers: multiply by 100, divide result |
| Hardcoding `range(5)` | Use `num_days` / `num_hours` parameters |
| Non-linear `x * y` | Use `model.AddMultiplicationEquality(z, [x, y])` |
| Ignoring `FEASIBLE` status | Still a valid solution; increase timeout if optimal needed |
| Group name mismatch (`"1ºA"` vs `"1º-A"`) | Use `normalize_group_name()` |
| Subject in multiple SubjectGroups | Invalid — causes conflicting constraints |
| Missing `__init__.py` import | Restriction silently not used |
| Missing `scheduler.py` wiring | Restriction silently not used |

---

## 11. Gap Minimization & Even Distribution (Future Work)

These constraints are described in `CONSTRAINTS.md` and the Gherkin scenarios
but are not yet implemented. They are good candidates for the next restriction
to add:

### Gap minimization
Penalize empty hours between scheduled blocks for a teacher or group in a day.
Use busy-hour BoolVars + gap-detection with `busy[h] - busy[h+1]` and check
that busy hours exist later in the day.

### Even distribution
Avoid concentrating all hours of a subject on a single day.
Use `AddMaxEquality` / `AddMinEquality` to compute spread across days, then
penalize the spread in the objective.

See §4.5 for the aggregation pattern needed by both.
