from ortools.sat.python import cp_model

from restrictions.joint_class_assignment import JointClassAssignment


class MockTeacher:
    def __init__(self, id, name="Test", subjects=None, max_hours_week=20):
        self.id = id
        self.name = name
        self.subjects = subjects or []
        self.max_hours_week = max_hours_week


class MockSubject:
    def __init__(self, id, name="Test", course_id="6", weekly_hours=2):
        self.id = id
        self.name = name
        self.course_id = course_id
        self.weekly_hours = weekly_hours


class MockJointClass:
    def __init__(self, id=1, course_id="6", subject_id="LEN6",
                 teacher_id="t1", lines=None, shared_hours=None):
        self.id = id
        self.course_id = course_id
        self.subject_id = subject_id
        self.teacher_id = teacher_id
        self.lines = lines or ["B", "C"]
        self.shared_hours = shared_hours


def test_joint_class_fixed_teacher_feasible():
    model = cp_model.CpModel()
    num_days = 2
    num_hours = 2

    subject = MockSubject(id="LEN6", weekly_hours=2)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-A", "6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        for d in range(num_days):
            for h in range(num_hours):
                key = (group, "LEN6", "t1", d, h)
                assignments[key] = model.NewBoolVar(
                    f"g:{group} sub:LEN6 t:t1 d:{d} h:{h}"
                )

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["B", "C"])
    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def test_joint_class_fixed_teacher_enforces_equality():
    model = cp_model.CpModel()
    num_days = 1
    num_hours = 2

    subject = MockSubject(id="LEN6", weekly_hours=2)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        for d in range(num_days):
            for h in range(num_hours):
                key = (group, "LEN6", "t1", d, h)
                assignments[key] = model.NewBoolVar(
                    f"g:{group} sub:LEN6 t:t1 d:{d} h:{h}"
                )

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["B", "C"])
    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )

    # Force one specific hour to be active to make the equality check meaningful
    model.Add(assignments[("6-B", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-C", "LEN6", "t1", 0, 1)] == 0)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    for d in range(num_days):
        for h in range(num_hours):
            val_b = solver.Value(assignments[("6-B", "LEN6", "t1", d, h)])
            val_c = solver.Value(assignments[("6-C", "LEN6", "t1", d, h)])
            assert val_b == val_c, (
                f"Joint class equality violated at d={d} h={h}: "
                f"6-B={val_b}, 6-C={val_c}"
            )


def test_joint_class_fixed_teacher_total_hours_match():
    model = cp_model.CpModel()
    num_days = 5
    num_hours = 2

    subject = MockSubject(id="LEN6", weekly_hours=4)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        for d in range(num_days):
            for h in range(num_hours):
                key = (group, "LEN6", "t1", d, h)
                assignments[key] = model.NewBoolVar(
                    f"g:{group} sub:LEN6 t:t1 d:{d} h:{h}"
                )

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["B", "C"])
    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )

    for group in ["6-B", "6-C"]:
        total = sum(
            assignments[(group, "LEN6", "t1", d, h)]
            for d in range(num_days)
            for h in range(num_hours)
        )
        model.Add(total == 4)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    hours_b = sum(
        solver.Value(assignments[("6-B", "LEN6", "t1", d, h)])
        for d in range(num_days)
        for h in range(num_hours)
    )
    hours_c = sum(
        solver.Value(assignments[("6-C", "LEN6", "t1", d, h)])
        for d in range(num_days)
        for h in range(num_hours)
    )
    assert hours_b == 4, f"6-B should have 4 hours, got {hours_b}"
    assert hours_c == 4, f"6-C should have 4 hours, got {hours_c}"


def test_joint_class_fixed_teacher_with_teacher_one_class():
    from restrictions.teacher_one_class_at_a_time import TeacherOneClassAtATime

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 1

    subject = MockSubject(id="LEN6", weekly_hours=1)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-A", "6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        key = (group, "LEN6", "t1", 0, 0)
        assignments[key] = model.NewBoolVar(f"g:{group} sub:LEN6 t:t1 d:0 h:0")
    # Non-joint class for same teacher at same slot
    assignments[("6-A", "MAT6", "t1", 0, 0)] = model.NewBoolVar(
        "g:6-A sub:MAT6 t:t1 d:0 h:0"
    )

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["B", "C"])
    joint_lookup = {}
    for tid in ["t1"]:
        joint_lookup[(tid, "LEN6", 0, 0)] = {
            "jc_id": jc.id,
            "num_lines": 2,
            "first_group": "6-B",
            "course_id": "6",
            "subject_id": "LEN6",
        }

    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )
    TeacherOneClassAtATime().apply(
        model, assignments, [teacher], num_days, num_hours,
        joint_lookup=joint_lookup,
    )

    # Force all three assignments to 1 — should be infeasible because
    # teacher can only teach one class, and the joint class counts as one
    model.Add(assignments[("6-B", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-C", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-A", "MAT6", "t1", 0, 0)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        "Expected infeasible: teacher cannot teach joint class + another class "
        "at same slot"
    )


def test_joint_class_fixed_teacher_allows_joint_and_non_joint_at_different_slots():
    from restrictions.teacher_one_class_at_a_time import TeacherOneClassAtATime

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 2

    subject = MockSubject(id="LEN6", weekly_hours=2)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-A", "6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        key = (group, "LEN6", "t1", 0, 0)
        assignments[key] = model.NewBoolVar(f"g:{group} sub:LEN6 t:t1 d:0 h:0")
    assignments[("6-A", "MAT6", "t1", 0, 1)] = model.NewBoolVar(
        "g:6-A sub:MAT6 t:t1 d:0 h:1"
    )

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["B", "C"])
    joint_lookup = {}
    for tid in ["t1"]:
        joint_lookup[(tid, "LEN6", 0, 0)] = {
            "jc_id": jc.id,
            "num_lines": 2,
            "first_group": "6-B",
            "course_id": "6",
            "subject_id": "LEN6",
        }

    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )
    TeacherOneClassAtATime().apply(
        model, assignments, [teacher], num_days, num_hours,
        joint_lookup=joint_lookup,
    )

    # Joint at slot 0, another class at slot 1 — should be feasible
    model.Add(assignments[("6-B", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-C", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-A", "MAT6", "t1", 0, 1)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
        "Expected feasible: joint class and another class at different slots"
    )


def test_joint_class_does_not_merge_non_joint_same_subject_same_slot():
    from restrictions.teacher_one_class_at_a_time import TeacherOneClassAtATime

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 1

    subject = MockSubject(id="LEN6", weekly_hours=1)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-A", "6-B", "6-C"]
    assignments = {}
    assignments[("6-B", "LEN6", "t1", 0, 0)] = model.NewBoolVar("g:6-B sub:LEN6 t:t1 d:0 h:0")
    assignments[("6-C", "LEN6", "t1", 0, 0)] = model.NewBoolVar("g:6-C sub:LEN6 t:t1 d:0 h:0")
    # Same teacher+subject+slot but this group is NOT part of the joint class.
    assignments[("6-A", "LEN6", "t1", 0, 0)] = model.NewBoolVar("g:6-A sub:LEN6 t:t1 d:0 h:0")

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["B", "C"])
    joint_lookup = {
        ("t1", "LEN6", 0, 0): {
            "jc_id": jc.id,
            "num_lines": 2,
            "first_group": "6-B",
            "groups": ["6-B", "6-C"],
            "course_id": "6",
            "subject_id": "LEN6",
        }
    }

    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )
    TeacherOneClassAtATime().apply(
        model, assignments, [teacher], num_days, num_hours,
        joint_lookup=joint_lookup,
    )

    # The joint class counts as one logical class, but 6-A is a second class.
    model.Add(assignments[("6-B", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-C", "LEN6", "t1", 0, 0)] == 1)
    model.Add(assignments[("6-A", "LEN6", "t1", 0, 0)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        "Expected infeasible: non-joint group at same slot must not be merged "
        "with the joint class"
    )


def test_joint_class_solver_chooses_teacher():
    model = cp_model.CpModel()
    num_days = 1
    num_hours = 2

    subject = MockSubject(id="LEN6", weekly_hours=2)
    t1 = MockTeacher(id="t1", subjects=[subject])
    t2 = MockTeacher(id="t2", subjects=[subject])

    all_groups = ["6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        for teacher_id in ["t1", "t2"]:
            for d in range(num_days):
                for h in range(num_hours):
                    key = (group, "LEN6", teacher_id, d, h)
                    assignments[key] = model.NewBoolVar(
                        f"g:{group} sub:LEN6 t:{teacher_id} d:{d} h:{h}"
                    )

    jc = MockJointClass(
        subject_id="LEN6", teacher_id=None, lines=["B", "C"],
    )
    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [t1, t2],
    )

    # Force at least one assignment so solver picks a teacher
    model.Add(assignments[("6-B", "LEN6", "t1", 0, 0)] +
              assignments[("6-B", "LEN6", "t2", 0, 0)] >= 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def test_joint_class_solver_chooses_teacher_same_teacher():
    model = cp_model.CpModel()
    num_days = 1
    num_hours = 1

    subject = MockSubject(id="LEN6", weekly_hours=1)
    t1 = MockTeacher(id="t1", subjects=[subject])
    t2 = MockTeacher(id="t2", subjects=[subject])

    all_groups = ["6-B", "6-C"]
    assignments = {}
    for group in ["6-B", "6-C"]:
        for teacher_id in ["t1", "t2"]:
            key = (group, "LEN6", teacher_id, 0, 0)
            assignments[key] = model.NewBoolVar(
                f"g:{group} sub:LEN6 t:{teacher_id} d:0 h:0"
            )

    jc = MockJointClass(
        subject_id="LEN6", teacher_id=None, lines=["B", "C"],
    )
    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [t1, t2],
    )

    # Force at least one hour to be assigned so we can verify teacher equality
    model.Add(assignments[("6-B", "LEN6", "t1", 0, 0)] + assignments[("6-B", "LEN6", "t2", 0, 0)] >= 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    val_b_t1 = solver.Value(assignments[("6-B", "LEN6", "t1", 0, 0)])
    val_b_t2 = solver.Value(assignments[("6-B", "LEN6", "t2", 0, 0)])
    val_c_t1 = solver.Value(assignments[("6-C", "LEN6", "t1", 0, 0)])
    val_c_t2 = solver.Value(assignments[("6-C", "LEN6", "t2", 0, 0)])

    teacher_for_b = "t1" if val_b_t1 == 1 else ("t2" if val_b_t2 == 1 else None)
    teacher_for_c = "t1" if val_c_t1 == 1 else ("t2" if val_c_t2 == 1 else None)

    assert teacher_for_b is not None, "6-B must have a teacher assigned"
    assert teacher_for_c is not None, "6-C must have a teacher assigned"
    assert teacher_for_b == teacher_for_c, (
        f"Both groups must have the same teacher: 6-B={teacher_for_b}, "
        f"6-C={teacher_for_c}"
    )


def test_joint_class_three_lines():
    model = cp_model.CpModel()
    num_days = 1
    num_hours = 1

    subject = MockSubject(id="LEN6", weekly_hours=1)
    teacher = MockTeacher(id="t1", subjects=[subject])

    all_groups = ["6-A", "6-B", "6-C"]
    assignments = {}
    for group in ["6-A", "6-B", "6-C"]:
        key = (group, "LEN6", "t1", 0, 0)
        assignments[key] = model.NewBoolVar(f"g:{group} sub:LEN6 t:t1 d:0 h:0")

    jc = MockJointClass(subject_id="LEN6", teacher_id="t1", lines=["A", "B", "C"])
    JointClassAssignment().apply(
        model, assignments, all_groups, num_days, num_hours,
        [jc], [teacher],
    )

    # Force assignment to verify equality across all three
    model.Add(assignments[("6-A", "LEN6", "t1", 0, 0)] == 1)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    val_a = solver.Value(assignments[("6-A", "LEN6", "t1", 0, 0)])
    val_b = solver.Value(assignments[("6-B", "LEN6", "t1", 0, 0)])
    val_c = solver.Value(assignments[("6-C", "LEN6", "t1", 0, 0)])
    assert val_a == val_b == val_c, (
        f"All three lines must be equal: A={val_a}, B={val_b}, C={val_c}"
    )
