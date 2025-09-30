from ortools.sat.python import cp_model


def test_teacher_max_weekly_hours_allows_within_limit():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithMax:
        def __init__(self, id, max_hours_week):
            self.id = id
            self.max_hours_week = max_hours_week

    teacher = MockTeacherWithMax(id="t1", max_hours_week=2)

    # Create three potential assignment slots but only two need to be set to satisfy limit
    assignments = {}
    assignments[("g1", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("g1", "s1", "t1", 0, 1)] = model.NewBoolVar("a1")
    assignments[("g1", "s1", "t1", 1, 0)] = model.NewBoolVar("a2")

    # Apply weekly-hours restriction
    TeacherMaxWeeklyHours().apply(model, assignments, [teacher])

    # Also add constraint to set two of them to 1 (which is within max_hours_week)
    model.Add(assignments[("g1", "s1", "t1", 0, 0)] + assignments[("g1", "s1", "t1", 0, 1)] == 2)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_teacher_max_weekly_hours_blocks_overload():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithMax:
        def __init__(self, id, max_hours_week):
            self.id = id
            self.max_hours_week = max_hours_week

    teacher = MockTeacherWithMax(id="t1", max_hours_week=1)

    assignments = {}
    # two assignments in the same week, but max is 1
    assignments[("g1", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("g2", "s2", "t1", 0, 1)] = model.NewBoolVar("a1")

    # Force both to 1 which should violate the weekly max_hours_week==1
    model.Add(assignments[("g1", "s1", "t1", 0, 0)] == 1)
    model.Add(assignments[("g2", "s2", "t1", 0, 1)] == 1)

    TeacherMaxWeeklyHours().apply(model, assignments, [teacher])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE
