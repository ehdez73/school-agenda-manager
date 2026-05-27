from ortools.sat.python import cp_model


class MockSubject:
    def __init__(self, id, course_id, weekly_hours, teach_every_day=False):
        self.id = id
        self.course_id = course_id
        self.weekly_hours = weekly_hours
        self.teach_every_day = teach_every_day


def test_teach_every_day_subject_covers_all_days():
    from restrictions import SubjectMustEveryDay

    model = cp_model.CpModel()
    num_days = 3

    subject = MockSubject(id="math", course_id="1", weekly_hours=3,
                          teach_every_day=True)
    groups = ["1-A"]
    subjects = [subject]

    assignments = {}
    for d in range(num_days):
        for h in range(2):
            key = ("1-A", "math", "t1", d, h)
            assignments[key] = model.NewBoolVar(f"a_{d}_{h}")

    SubjectMustEveryDay().apply(model, assignments, groups, subjects, num_days)

    # Force all hours into day 0 — should violate teach-every-day
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "math", "t1", 0, 1)] == 1)
    model.Add(assignments[("1-A", "math", "t1", 1, 0)] == 0)
    model.Add(assignments[("1-A", "math", "t1", 1, 1)] == 0)
    model.Add(assignments[("1-A", "math", "t1", 2, 0)] == 0)
    model.Add(assignments[("1-A", "math", "t1", 2, 1)] == 0)
    model.Add(sum(assignments.values()) == 2)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_teach_every_day_skips_non_flagged():
    from restrictions import SubjectMustEveryDay

    model = cp_model.CpModel()
    num_days = 3

    subject = MockSubject(id="math", course_id="1", weekly_hours=2,
                          teach_every_day=False)
    groups = ["1-A"]
    subjects = [subject]

    assignments = {}
    for d in range(num_days):
        for h in range(2):
            key = ("1-A", "math", "t1", d, h)
            assignments[key] = model.NewBoolVar(f"a_{d}_{h}")

    SubjectMustEveryDay().apply(model, assignments, groups, subjects, num_days)

    # All hours on day 0 — no constraint so should be fine
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "math", "t1", 0, 1)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_teach_every_day_subject_skips_other_courses():
    from restrictions import SubjectMustEveryDay

    model = cp_model.CpModel()
    num_days = 2

    subject = MockSubject(id="math", course_id="1", weekly_hours=2,
                          teach_every_day=True)
    groups = ["2-A"]  # Different course from subject
    subjects = [subject]

    assignments = {
        ("2-A", "math", "t1", 0, 0): model.NewBoolVar("a0"),
        ("2-A", "math", "t1", 0, 1): model.NewBoolVar("a1"),
    }

    SubjectMustEveryDay().apply(model, assignments, groups, subjects, num_days)

    # All hours on day 0 — subject is course 1, group is course 2, no constraint
    model.Add(assignments[("2-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("2-A", "math", "t1", 0, 1)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_teach_every_day_no_variables_skips_silently():
    from restrictions import SubjectMustEveryDay

    model = cp_model.CpModel()
    num_days = 2

    subject = MockSubject(id="math", course_id="1", weekly_hours=2,
                          teach_every_day=True)
    groups = ["1-A"]
    subjects = [subject]

    # No assignment vars for this subject at all (e.g., no teacher assigned)
    assignments = {}

    # Should not crash
    SubjectMustEveryDay().apply(model, assignments, groups, subjects, num_days)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
