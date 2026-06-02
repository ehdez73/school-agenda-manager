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


def test_coordination_hours_reduces_capacity():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithCoord:
        def __init__(self, id, max_hours_week, coordination_hours):
            self.id = id
            self.max_hours_week = max_hours_week
            self.coordination_hours = coordination_hours

    teacher = MockTeacherWithCoord(id="t1", max_hours_week=5, coordination_hours=2)

    assignments = {}
    # 4 teaching assignments — 4 > effective_max(3) so should be infeasible
    for i in range(4):
        assignments[("g1", "s1", "t1", 0, i)] = model.NewBoolVar(f"a{i}")
        model.Add(assignments[("g1", "s1", "t1", 0, i)] == 1)

    TeacherMaxWeeklyHours().apply(model, assignments, [teacher])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_coordination_hours_allows_effective_max():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithCoord:
        def __init__(self, id, max_hours_week, coordination_hours):
            self.id = id
            self.max_hours_week = max_hours_week
            self.coordination_hours = coordination_hours

    teacher = MockTeacherWithCoord(id="t1", max_hours_week=5, coordination_hours=2)

    assignments = {}
    # 3 teaching assignments — 3 <= effective_max(3) so should be feasible
    for i in range(3):
        assignments[("g1", "s1", "t1", 0, i)] = model.NewBoolVar(f"a{i}")
        model.Add(assignments[("g1", "s1", "t1", 0, i)] == 1)

    TeacherMaxWeeklyHours().apply(model, assignments, [teacher])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.FEASIBLE, cp_model.OPTIMAL)


def test_joint_class_counted_once_in_teacher_max_hours():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithMax:
        def __init__(self, id, max_hours_week):
            self.id = id
            self.max_hours_week = max_hours_week

    teacher = MockTeacherWithMax(id="t1", max_hours_week=3)

    assignments = {}
    # 2 joint assignments (one per group) at slot 0,0
    # and 2 joint assignments at slot 0,1
    # and 1 non-joint at slot 0,2
    # With joint counting: 2 joint + 1 non-joint = 3 hours (within limit)
    # Without joint counting (raw): 2*2 + 1 = 5 hours (over limit)
    for group in ["g1", "g2"]:
        assignments[(group, "s1", "t1", 0, 0)] = model.NewBoolVar(f"{group}_0_0")
        assignments[(group, "s1", "t1", 0, 1)] = model.NewBoolVar(f"{group}_0_1")
    assignments[("g3", "s2", "t1", 0, 2)] = model.NewBoolVar("g3_0_2")

    # Force all assignments to 1
    for key in assignments:
        model.Add(assignments[key] == 1)

    # Joint lookup: (t1, s1, 0, 0) and (t1, s1, 0, 1) are joint with 2 lines
    joint_lookup = {
        ("t1", "s1", 0, 0): {"num_lines": 2, "first_group": "g1"},
        ("t1", "s1", 0, 1): {"num_lines": 2, "first_group": "g1"},
    }

    TeacherMaxWeeklyHours().apply(model, assignments, [teacher],
                                  joint_lookup=joint_lookup)

    # With proper joint counting (2 joint slots + 1 non-joint = 3), should be feasible
    # Without joint counting (4 + 1 = 5 > 3), would be infeasible
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.FEASIBLE, cp_model.OPTIMAL), (
        "Expected feasible: joint classes should be counted once, not per-group"
    )


def test_joint_class_not_double_counted_non_joint():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithMax:
        def __init__(self, id, max_hours_week):
            self.id = id
            self.max_hours_week = max_hours_week

    teacher = MockTeacherWithMax(id="t1", max_hours_week=1)

    assignments = {}
    # Two different subjects (non-joint) at different slots — should count as 2
    assignments[("g1", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("g2", "s2", "t1", 0, 1)] = model.NewBoolVar("a1")

    model.Add(assignments[("g1", "s1", "t1", 0, 0)] == 1)
    model.Add(assignments[("g2", "s2", "t1", 0, 1)] == 1)

    # Empty joint lookup — no joint classes
    TeacherMaxWeeklyHours().apply(model, assignments, [teacher],
                                  joint_lookup={})

    # 2 non-joint hours with max_hours_week=1 should be infeasible
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        "Expected infeasible: 2 non-joint hours exceed max 1"
    )


def test_joint_class_does_not_hide_non_joint_same_subject_same_slot_in_max_hours():
    from restrictions import TeacherMaxWeeklyHours

    model = cp_model.CpModel()

    class MockTeacherWithMax:
        def __init__(self, id, max_hours_week):
            self.id = id
            self.max_hours_week = max_hours_week

    teacher = MockTeacherWithMax(id="t1", max_hours_week=1)

    assignments = {}
    # Joint class members.
    assignments[("6-B", "LEN6", "t1", 0, 0)] = model.NewBoolVar("b")
    assignments[("6-C", "LEN6", "t1", 0, 0)] = model.NewBoolVar("c")
    # Same teacher+subject+slot but non-joint group.
    assignments[("6-A", "LEN6", "t1", 0, 0)] = model.NewBoolVar("a")

    for key in assignments:
        model.Add(assignments[key] == 1)

    joint_lookup = {
        ("t1", "LEN6", 0, 0): {
            "jc_id": 1,
            "num_lines": 2,
            "first_group": "6-B",
            "groups": ["6-B", "6-C"],
            "course_id": "6",
            "subject_id": "LEN6",
        }
    }

    TeacherMaxWeeklyHours().apply(model, assignments, [teacher],
                                  joint_lookup=joint_lookup)

    # Correct logical count is 2: (joint B+C) + (non-joint A).
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        "Expected infeasible: non-joint assignment must be counted separately "
        "from the joint class"
    )
