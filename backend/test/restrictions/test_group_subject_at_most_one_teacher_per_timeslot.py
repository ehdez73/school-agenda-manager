from ortools.sat.python import cp_model


def test_blocks_two_teachers_for_same_group_subject_timeslot():
    from restrictions import GroupSubjectAtMostOneTeacherPerTimeslot

    model = cp_model.CpModel()
    assignments = {
        ("5-A", "ING5", "t1", 0, 0): model.NewBoolVar("a_t1"),
        ("5-A", "ING5", "t2", 0, 0): model.NewBoolVar("a_t2"),
    }

    model.Add(assignments[("5-A", "ING5", "t1", 0, 0)] == 1)
    model.Add(assignments[("5-A", "ING5", "t2", 0, 0)] == 1)

    GroupSubjectAtMostOneTeacherPerTimeslot().apply(
        model, assignments, ["5-A"], 1, 1
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_allows_two_teachers_for_same_subject_in_different_slots():
    from restrictions import GroupSubjectAtMostOneTeacherPerTimeslot

    model = cp_model.CpModel()
    assignments = {
        ("5-A", "ING5", "t1", 0, 0): model.NewBoolVar("a_t1_h0"),
        ("5-A", "ING5", "t2", 0, 1): model.NewBoolVar("a_t2_h1"),
    }

    model.Add(assignments[("5-A", "ING5", "t1", 0, 0)] == 1)
    model.Add(assignments[("5-A", "ING5", "t2", 0, 1)] == 1)

    GroupSubjectAtMostOneTeacherPerTimeslot().apply(
        model, assignments, ["5-A"], 1, 2
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_allows_two_groups_same_subject_same_slot_with_different_teachers():
    from restrictions import GroupSubjectAtMostOneTeacherPerTimeslot

    model = cp_model.CpModel()
    assignments = {
        ("5-A", "ING5", "t1", 0, 0): model.NewBoolVar("a_5a_t1"),
        ("5-B", "ING5", "t2", 0, 0): model.NewBoolVar("a_5b_t2"),
    }

    model.Add(assignments[("5-A", "ING5", "t1", 0, 0)] == 1)
    model.Add(assignments[("5-B", "ING5", "t2", 0, 0)] == 1)

    GroupSubjectAtMostOneTeacherPerTimeslot().apply(
        model, assignments, ["5-A", "5-B"], 1, 1
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
