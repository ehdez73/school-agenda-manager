from ortools.sat.python import cp_model


class MockSubject:
    def __init__(self, id, max_hours_per_day):
        self.id = id
        self.max_hours_per_day = max_hours_per_day


def test_subject_max_hours_allows_within_limit():
    from backend.restrictions.subject_max_hours_per_day import SubjectMaxHoursPerDay

    model = cp_model.CpModel()

    subject = MockSubject(id="math", max_hours_per_day=2)
    num_days = 1

    assignments = {
        ("g1", "math", "t1", 0, 0): model.NewBoolVar("a0"),
        ("g1", "math", "t1", 0, 1): model.NewBoolVar("a1"),
        ("g1", "math", "t1", 0, 2): model.NewBoolVar("a2"),
    }

    SubjectMaxHoursPerDay().apply(model, assignments, [subject], num_days)

    # Force two assignments on day 0 — should be allowed (max=2)
    model.Add(assignments[("g1", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("g1", "math", "t1", 0, 1)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_subject_max_hours_blocks_over_limit():
    from backend.restrictions.subject_max_hours_per_day import SubjectMaxHoursPerDay

    model = cp_model.CpModel()

    subject = MockSubject(id="math", max_hours_per_day=1)
    num_days = 1

    assignments = {
        ("g1", "math", "t1", 0, 0): model.NewBoolVar("a0"),
        ("g1", "math", "t1", 0, 1): model.NewBoolVar("a1"),
    }

    SubjectMaxHoursPerDay().apply(model, assignments, [subject], num_days)

    # Force two assignments on day 0 — should violate max=1
    model.Add(assignments[("g1", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("g1", "math", "t1", 0, 1)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_subject_max_hours_multiple_days():
    from backend.restrictions.subject_max_hours_per_day import SubjectMaxHoursPerDay

    model = cp_model.CpModel()

    subject = MockSubject(id="math", max_hours_per_day=1)
    num_days = 2

    assignments = {
        ("g1", "math", "t1", 0, 0): model.NewBoolVar("a0"),
        ("g1", "math", "t1", 1, 0): model.NewBoolVar("a1"),
    }

    SubjectMaxHoursPerDay().apply(model, assignments, [subject], num_days)

    # One hour on day 0 and one on day 1 — each day within limit
    model.Add(assignments[("g1", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("g1", "math", "t1", 1, 0)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
