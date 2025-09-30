from ortools.sat.python import cp_model
import json


class MockTeacher:
    def __init__(self, id, preferences=None):
        self.id = id
        self.preferences = preferences


def _make_assignments(model, groups, teacher_id, days=1, hours=3):
    assignments = {}
    for g in groups:
        for d in range(days):
            for h in range(hours):
                key = (g, "s1", teacher_id, d, h)
                assignments[key] = model.NewBoolVar(f"a_{g}_{d}_{h}")
    return assignments


def test_teacher_unavailable_blocks_unavailable_hours():
    from restrictions import TeacherUnavailableTimes

    model = cp_model.CpModel()
    teacher = MockTeacher(id="t1", preferences=json.dumps({"0": {"unavailable": [1]}}))
    groups = ["1-A"]
    assignments = _make_assignments(model, groups, teacher.id, days=1, hours=3)

    # Force an assignment at the unavailable hour
    model.Add(assignments[("1-A", "s1", teacher.id, 0, 1)] == 1)

    TeacherUnavailableTimes().apply(model, assignments, [teacher], num_days=1, num_hours=3)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_teacher_unavailable_ignores_malformed_preferences():
    from restrictions import TeacherUnavailableTimes

    model = cp_model.CpModel()
    # malformed JSON should be skipped
    teacher = MockTeacher(id="t_bad", preferences="not-json")
    groups = ["1-A"]
    assignments = _make_assignments(model, groups, teacher.id, days=1, hours=2)

    # Force an assignment - since prefs are malformed, no constraint should be added
    model.Add(assignments[("1-A", "s1", teacher.id, 0, 0)] == 1)

    TeacherUnavailableTimes().apply(model, assignments, [teacher], num_days=1, num_hours=2)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_teacher_unavailable_ignores_out_of_range_hours():
    from restrictions import TeacherUnavailableTimes

    model = cp_model.CpModel()
    # unavailable refers to hour 99 which is out of range and should be ignored
    teacher = MockTeacher(id="t1", preferences=json.dumps({"0": {"unavailable": [99]}}))
    groups = ["1-A"]
    assignments = _make_assignments(model, groups, teacher.id, days=1, hours=3)

    # Force assignment in normal slot; should be allowed because unavailable hour is out of range
    model.Add(assignments[("1-A", "s1", teacher.id, 0, 1)] == 1)

    TeacherUnavailableTimes().apply(model, assignments, [teacher], num_days=1, num_hours=3)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
