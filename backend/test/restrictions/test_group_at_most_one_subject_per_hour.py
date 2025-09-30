from ortools.sat.python import cp_model
from ..schemas import TestSubject, TestSubjectGroup


def _make_vars_for_subjects(model, groups, subjects, days=1, hours=1):
    assignments = {}
    for group in groups:
        for subject in subjects:
            for d in range(days):
                for h in range(hours):
                    key = (group, subject.id, "t1", d, h)
                    assignments[key] = model.NewBoolVar(f"assign_{group}_{subject.id}_{d}_{h}")
    return assignments


def test_allows_single_standalone_subject():
    """A single standalone subject in a timeslot should be allowed."""
    from restrictions import GroupAtMostOneSubjectPerHour

    model = cp_model.CpModel()
    groups = ["1-A"]

    s = TestSubject(id="math", course_id="1", weekly_hours=1, subjectgroup_id=None)
    all_subjects = [s]
    all_subjectgroups = []

    assignments = _make_vars_for_subjects(model, groups, all_subjects, days=1, hours=1)

    # Force the single standalone subject to be assigned in the only slot
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    GroupAtMostOneSubjectPerHour().apply(model, assignments, groups, 1, 1, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_blocks_two_standalone_subjects_same_slot():
    """Two standalone subjects in the same timeslot should be infeasible."""
    from restrictions import GroupAtMostOneSubjectPerHour

    model = cp_model.CpModel()
    groups = ["1-A"]

    s1 = TestSubject(id="math", course_id="1", weekly_hours=1, subjectgroup_id=None)
    s2 = TestSubject(id="science", course_id="1", weekly_hours=1, subjectgroup_id=None)
    all_subjects = [s1, s2]
    all_subjectgroups = []

    assignments = _make_vars_for_subjects(model, groups, all_subjects, days=1, hours=1)

    # Force both standalone subjects into the same slot
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "science", "t1", 0, 0)] == 1)

    GroupAtMostOneSubjectPerHour().apply(model, assignments, groups, 1, 1, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_allows_subjectgroup_members_together():
    """All members of a SubjectGroup are allowed together in the same slot."""
    from restrictions import GroupAtMostOneSubjectPerHour

    model = cp_model.CpModel()
    groups = ["1-A"]

    s1 = TestSubject(id="religion", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    s2 = TestSubject(id="ethics", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    all_subjects = [s1, s2]

    sg = TestSubjectGroup(id="sg1", subject_ids=["religion", "ethics"])
    all_subjectgroups = [sg]

    assignments = _make_vars_for_subjects(model, groups, all_subjects, days=1, hours=1)

    # Force one subject from the group to be assigned
    model.Add(assignments[("1-A", "religion", "t1", 0, 0)] == 1)

    GroupAtMostOneSubjectPerHour().apply(model, assignments, groups, 1, 1, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Should be feasible and the other member should be allowed (not required by this restriction)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_subjectgroup_conflicts_with_standalone():
    """A SubjectGroup (any member assigned) should conflict with a standalone subject in same slot."""
    from restrictions import GroupAtMostOneSubjectPerHour

    model = cp_model.CpModel()
    groups = ["1-A"]

    # SubjectGroup with two subjects + one standalone subject
    s1 = TestSubject(id="religion", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    s2 = TestSubject(id="ethics", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    s3 = TestSubject(id="math", course_id="1", weekly_hours=1, subjectgroup_id=None)
    all_subjects = [s1, s2, s3]

    sg = TestSubjectGroup(id="sg1", subject_ids=["religion", "ethics"])
    all_subjectgroups = [sg]

    assignments = _make_vars_for_subjects(model, groups, all_subjects, days=1, hours=1)

    # Force a SubjectGroup member and the standalone subject in same slot
    model.Add(assignments[("1-A", "religion", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    GroupAtMostOneSubjectPerHour().apply(model, assignments, groups, 1, 1, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE
