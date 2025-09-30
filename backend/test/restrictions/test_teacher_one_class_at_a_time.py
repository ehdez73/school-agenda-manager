from ortools.sat.python import cp_model


class MockTeacher:
    def __init__(self, id):
        self.id = id


def test_teacher_one_class_at_a_time_allows_single_assignment():
    from restrictions import TeacherOneClassAtATime

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 2

    # Create one teacher and one group/subject assignment variables
    teacher = MockTeacher(id="t1")
    assignments = {}
    # group, subject, teacher, day, hour
    assignments[("g1", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("g1", "s1", "t1", 0, 1)] = model.NewBoolVar("a1")

    # Apply restriction
    TeacherOneClassAtATime().apply(model, assignments, [teacher], num_days, num_hours)

    # No further constraints - solver should be able to pick any combination
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_teacher_one_class_at_a_time_blocks_two_simultaneous():
    from restrictions import TeacherOneClassAtATime

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 1

    teacher = MockTeacher(id="t1")
    assignments = {}
    # two groups same teacher same day/hour
    assignments[("g1", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("g2", "s2", "t1", 0, 0)] = model.NewBoolVar("a1")

    # Add constraint that both a0 and a1 must be 1 to force conflict
    model.Add(assignments[("g1", "s1", "t1", 0, 0)] == 1)
    model.Add(assignments[("g2", "s2", "t1", 0, 0)] == 1)

    TeacherOneClassAtATime().apply(model, assignments, [teacher], num_days, num_hours)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    # Infeasible because teacher cannot be in two places at once
    assert status == cp_model.INFEASIBLE
