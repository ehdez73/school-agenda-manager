from ortools.sat.python import cp_model
from ..schemas import TestSubject, TestSubjectGroup


def _make_assignments(model, groups, subjects, days=1, hours=1):
    assignments = {}
    for group in groups:
        for subject in subjects:
            for d in range(days):
                for h in range(hours):
                    key = (group, subject.id, "t1", d, h)
                    assignments[key] = model.NewBoolVar(
                        f"a_{group}_{subject.id}_{d}_{h}")
    return assignments


def test_allows_single_standalone_subject():
    from restrictions import GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]

    s = TestSubject(id="math", course_id="1", weekly_hours=2)
    all_subjects = [s]

    assignments = _make_assignments(model, groups, all_subjects, days=1, hours=2)

    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 1, 2, []
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_blocks_two_standalone_subjects_same_slot():
    from restrictions import GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]

    s1 = TestSubject(id="math", course_id="1", weekly_hours=1)
    s2 = TestSubject(id="science", course_id="1", weekly_hours=1)
    all_subjects = [s1, s2]

    assignments = _make_assignments(model, groups, all_subjects, days=1, hours=1)

    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "science", "t1", 0, 0)] == 1)

    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 1, 1, []
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_allows_subjectgroup_together():
    from restrictions import GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]

    s1 = TestSubject(id="rel", course_id="1", weekly_hours=1,
                     subjectgroup_id="sg1")
    s2 = TestSubject(id="eth", course_id="1", weekly_hours=1,
                     subjectgroup_id="sg1")
    all_subjects = [s1, s2]

    sg = TestSubjectGroup(id="sg1", subject_ids=["rel", "eth"])
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, all_subjects, days=1, hours=1)

    model.Add(assignments[("1-A", "rel", "t1", 0, 0)] == 1)

    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 1, 1, all_subjectgroups
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL

    # The SubjectGroup subjects share a slot; verify both can be active
    solver2 = cp_model.CpSolver()
    model2 = cp_model.CpModel()
    assignments2 = _make_assignments(model2, groups, all_subjects, days=1, hours=1)
    model2.Add(assignments2[("1-A", "rel", "t1", 0, 0)] == 1)
    model2.Add(assignments2[("1-A", "eth", "t1", 0, 0)] == 1)
    GroupAtMostOneLogicalAssignment().apply(
        model2, assignments2, groups, 1, 1, all_subjectgroups
    )
    status2 = solver2.Solve(model2)
    # Both should be feasible since they're in the same logical unit
    assert status2 == cp_model.FEASIBLE or status2 == cp_model.OPTIMAL


def test_subjectgroup_conflicts_with_standalone():
    from restrictions import GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]

    s1 = TestSubject(id="rel", course_id="1", weekly_hours=1,
                     subjectgroup_id="sg1")
    s2 = TestSubject(id="eth", course_id="1", weekly_hours=1,
                     subjectgroup_id="sg1")
    s3 = TestSubject(id="math", course_id="1", weekly_hours=1,
                     subjectgroup_id=None)
    all_subjects = [s1, s2, s3]

    sg = TestSubjectGroup(id="sg1", subject_ids=["rel", "eth"])
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, all_subjects, days=1, hours=1)

    model.Add(assignments[("1-A", "rel", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 1, 1, all_subjectgroups
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_allows_different_slots_for_different_units():
    from restrictions import GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]

    s1 = TestSubject(id="math", course_id="1", weekly_hours=2)
    s2 = TestSubject(id="science", course_id="1", weekly_hours=2)
    all_subjects = [s1, s2]

    assignments = _make_assignments(model, groups, all_subjects, days=1, hours=2)

    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "science", "t1", 0, 1)] == 1)

    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 1, 2, []
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_no_subjectgroups_still_works():
    from restrictions import GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]

    s = TestSubject(id="math", course_id="1", weekly_hours=1)

    assignments = _make_assignments(model, groups, [s], days=1, hours=1)

    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 1, 1, None
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
