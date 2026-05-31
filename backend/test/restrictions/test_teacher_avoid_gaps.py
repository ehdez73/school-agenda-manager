import os
import sys

from ortools.sat.python import cp_model

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from ...restrictions.teacher_avoid_gaps import TeacherAvoidGaps  # noqa: E402


class MockTeacher:
    def __init__(self, teacher_id, name="Test"):
        self.id = teacher_id
        self.name = name


def _make_assignments(model, teacher, num_days, num_hours, groups=None, subject_id="math"):
    if groups is None:
        groups = ["1-A"]
    assignments = {}
    for group in groups:
        for d in range(num_days):
            for h in range(num_hours):
                key = (group, subject_id, teacher.id, d, h)
                assignments[key] = model.NewBoolVar(f"a_{group}_{d}_{h}")
    return assignments


def test_single_block_no_penalty():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=5)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(assignments[key("1-A", 0, 0)] == 1)
    model.Add(assignments[key("1-A", 0, 1)] == 1)
    model.Add(assignments[key("1-A", 0, 2)] == 1)
    model.Add(assignments[key("1-A", 0, 3)] == 0)
    model.Add(assignments[key("1-A", 0, 4)] == 0)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=5)

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == 0


def test_two_blocks_penalized():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=5)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(assignments[key("1-A", 0, 0)] == 1)
    model.Add(assignments[key("1-A", 0, 1)] == 1)
    model.Add(assignments[key("1-A", 0, 2)] == 0)
    model.Add(assignments[key("1-A", 0, 3)] == 1)
    model.Add(assignments[key("1-A", 0, 4)] == 1)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=5)

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == -10


def test_three_blocks_penalized_more():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=6)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(assignments[key("1-A", 0, 0)] == 1)
    model.Add(assignments[key("1-A", 0, 1)] == 0)
    model.Add(assignments[key("1-A", 0, 2)] == 1)
    model.Add(assignments[key("1-A", 0, 3)] == 0)
    model.Add(assignments[key("1-A", 0, 4)] == 1)
    model.Add(assignments[key("1-A", 0, 5)] == 0)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=6)

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == -20


def test_solver_prefers_single_block_over_gap():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=5)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(sum(assignments.values()) == 3)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=5)

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    assigned_hours = [
        h for h in range(5)
        if solver.Value(assignments[key("1-A", 0, h)]) == 1
    ]
    min_h, max_h = min(assigned_hours), max(assigned_hours)
    assert max_h - min_h + 1 == len(assigned_hours), (
        f"Expected contiguous block, got busy hours at {assigned_hours}"
    )


def test_no_classes_zero_penalty():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=5)

    for k in assignments:
        model.Add(assignments[k] == 0)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=5)

    assert len(restriction.preference_terms) == 1

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == 0


def test_multiple_days_penalty_is_per_day():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=2, num_hours=3)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(assignments[key("1-A", 0, 0)] == 1)
    model.Add(assignments[key("1-A", 0, 1)] == 1)
    model.Add(assignments[key("1-A", 0, 2)] == 1)

    model.Add(assignments[key("1-A", 1, 0)] == 1)
    model.Add(assignments[key("1-A", 1, 1)] == 0)
    model.Add(assignments[key("1-A", 1, 2)] == 1)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=2, num_hours=3)

    assert len(restriction.preference_terms) == 2

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == -10


def test_block_at_start_is_not_a_gap():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=5)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(assignments[key("1-A", 0, 0)] == 1)
    model.Add(assignments[key("1-A", 0, 1)] == 1)
    model.Add(assignments[key("1-A", 0, 2)] == 1)
    model.Add(assignments[key("1-A", 0, 3)] == 0)
    model.Add(assignments[key("1-A", 0, 4)] == 0)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=5)

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == 0


def test_block_at_end_is_not_a_gap():
    model = cp_model.CpModel()
    teacher = MockTeacher("t1")
    assignments = _make_assignments(model, teacher, num_days=1, num_hours=5)
    key = lambda g, d, h: (g, "math", teacher.id, d, h)

    model.Add(assignments[key("1-A", 0, 0)] == 0)
    model.Add(assignments[key("1-A", 0, 1)] == 0)
    model.Add(assignments[key("1-A", 0, 2)] == 1)
    model.Add(assignments[key("1-A", 0, 3)] == 1)
    model.Add(assignments[key("1-A", 0, 4)] == 1)

    restriction = TeacherAvoidGaps(weight=10)
    restriction.apply(model, assignments, [teacher], num_days=1, num_hours=5)

    model.Maximize(sum(restriction.preference_terms))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    total_penalty = sum(solver.Value(t) for t in restriction.preference_terms)
    assert total_penalty == 0
