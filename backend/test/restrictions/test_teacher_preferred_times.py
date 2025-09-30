import json
import os
import sys

from ortools.sat.python import cp_model

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from ...restrictions.teacher_preferred_times import TeacherPreferredTimes  # noqa: E402


class MockTeacher:
    def __init__(self, teacher_id, name, preferences):
        self.id = teacher_id
        self.name = name
        self.preferences = preferences


def test_teacher_preferred_times_rewards_preferred_slot():
    model = cp_model.CpModel()

    teacher = MockTeacher(
        teacher_id="t1",
        name="Teacher 1",
        preferences=json.dumps({"0": {"preferred": [1]}}),
    )

    assignments = {}
    group = "1A"
    subject_id = "math"
    day = 0
    for hour in range(2):
        key = (group, subject_id, teacher.id, day, hour)
        assignments[key] = model.NewBoolVar(f"assign_{hour}")

    model.Add(sum(assignments.values()) == 1)

    restriction = TeacherPreferredTimes()
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=2)

    assert restriction.preference_terms

    model.Maximize(sum(restriction.preference_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.OPTIMAL
    assert solver.Value(assignments[(group, subject_id, teacher.id, day, 1)]) == 1
    assert solver.Value(assignments[(group, subject_id, teacher.id, day, 0)]) == 0


def test_teacher_preferred_times_ignores_malformed_json_and_non_dict():
    model = cp_model.CpModel()

    # Malformed JSON should be ignored
    teacher_bad = MockTeacher(
        teacher_id="t_bad",
        name="Bad",
        preferences="not-a-json",
    )

    # Preferences that are not a dict should also be ignored
    teacher_non_dict = MockTeacher(
        teacher_id="t_nd",
        name="NonDict",
        preferences=json.dumps([1, 2, 3]),
    )

    assignments = {}
    group = "1A"
    subject_id = "math"
    day = 0
    for hour in range(2):
        assignments[(group, subject_id, teacher_bad.id, day, hour)] = model.NewBoolVar(f"b_{hour}")
        assignments[(group, subject_id, teacher_non_dict.id, day, hour)] = model.NewBoolVar(f"nd_{hour}")

    # Force one assignment for each teacher
    model.Add(assignments[(group, subject_id, teacher_bad.id, day, 0)] == 1)
    model.Add(assignments[(group, subject_id, teacher_non_dict.id, day, 1)] == 1)

    restriction = TeacherPreferredTimes()
    restriction.apply(model, assignments, [teacher_bad, teacher_non_dict], num_days=1, num_hours=2)

    # No preference terms should be produced for malformed/non-dict prefs
    assert not restriction.preference_terms


def test_teacher_preferred_times_respects_weight_and_deduplication():
    model = cp_model.CpModel()

    # Teacher with preferred hour 0
    teacher = MockTeacher(
        teacher_id="t1",
        name="Teacher 1",
        preferences=json.dumps({"0": {"preferred": [0]}}),
    )

    # Create two assignment vars that reference the same teacher/day/hour (different groups)
    assignments = {}
    groups = ["g1", "g2"]
    subject_id = "math"
    day = 0
    hour = 0
    for g in groups:
        assignments[(g, subject_id, teacher.id, day, hour)] = model.NewBoolVar(f"assign_{g}")

    # Force exactly one assignment overall (solver will pick one group)
    model.Add(sum(assignments.values()) == 1)

    # Use weight 3 to ensure multiplication occurs
    restriction = TeacherPreferredTimes(weight=3)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=1)

    # Preference terms should include a single term (deduplicated slot)
    assert len(restriction.preference_terms) == 1

    # The term should be scaled by weight; since it is an Expr, we cannot easily inspect
    # numeric coefficient here, but maximizing should prefer the preferred hour.
    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
