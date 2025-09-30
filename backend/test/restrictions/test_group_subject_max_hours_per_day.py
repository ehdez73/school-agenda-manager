from ortools.sat.python import cp_model


class MockSubject:
    def __init__(self, id, course_id, max_hours_per_day):
        self.id = id
        self.course_id = course_id
        self.max_hours_per_day = max_hours_per_day


class MockTeacher:
    def __init__(self, id, subjects):
        self.id = id
        self.subjects = subjects


def test_group_subject_max_hours_allows_within_limit():
    from restrictions import GroupSubjectMaxHoursPerDay

    model = cp_model.CpModel()
    num_days = 1

    subject = MockSubject(id="s1", course_id="1", max_hours_per_day=2)
    teacher = MockTeacher(id="t1", subjects=[subject])

    groups = ["1-A"]
    subjects = [subject]
    teachers = [teacher]

    assignments = {}
    # create three slots but only constrain sum <= 2
    assignments[("1-A", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("1-A", "s1", "t1", 0, 1)] = model.NewBoolVar("a1")
    assignments[("1-A", "s1", "t1", 0, 2)] = model.NewBoolVar("a2")

    GroupSubjectMaxHoursPerDay().apply(model, assignments, groups, subjects, teachers, num_days)

    # Force two to 1 which should be allowed
    model.Add(assignments[("1-A", "s1", "t1", 0, 0)] + assignments[("1-A", "s1", "t1", 0, 1)] == 2)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_group_subject_max_hours_blocks_over_limit():
    from restrictions import GroupSubjectMaxHoursPerDay

    model = cp_model.CpModel()
    num_days = 1

    subject = MockSubject(id="s1", course_id="1", max_hours_per_day=1)
    teacher = MockTeacher(id="t1", subjects=[subject])

    groups = ["1-A"]
    subjects = [subject]
    teachers = [teacher]

    assignments = {}
    assignments[("1-A", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("1-A", "s1", "t1", 0, 1)] = model.NewBoolVar("a1")

    # Force both to 1 which should exceed max_hours_per_day
    model.Add(assignments[("1-A", "s1", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "s1", "t1", 0, 1)] == 1)

    GroupSubjectMaxHoursPerDay().apply(model, assignments, groups, subjects, teachers, num_days)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE
