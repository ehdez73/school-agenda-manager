from ortools.sat.python import cp_model
from ..schemas import TestSubject, TestSubjectGroup


def _make_vars_for_subjects(model, groups, subjects, days=5, hours=5):
    assignments = {}
    for group in groups:
        for subject in subjects:
            for d in range(days):
                for h in range(hours):
                    key = (group, subject.id, "t1", d, h)
                    assignments[key] = model.NewBoolVar(f"assign_{group}_{subject.id}_{d}_{h}")
    return assignments


def test_subjectgroup_requires_all_or_none():
    """When one subject from a SubjectGroup is assigned, ALL subjects from that group must be assigned to the same timeslot."""
    from restrictions import SubjectGroupAssignment

    model = cp_model.CpModel()
    all_groups = ["1-A"]

    # Two subjects that belong to the same subjectgroup 'sg1'
    s1 = TestSubject(id="religion", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    s2 = TestSubject(id="ethics", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    all_subjects = [s1, s2]

    # Predefined subjectgroup that groups both subjects
    sg = TestSubjectGroup(id="sg1", subject_ids=["religion", "ethics"])
    all_subjectgroups = [sg]

    # Create variables but only use day=0,hour=0 for assertions
    assignments = _make_vars_for_subjects(model, all_groups, all_subjects, days=1, hours=1)

    # Force that exactly one of the subjectgroup members occupies slot (0,0)
    vars_in_slot = [assignments[("1-A", sid, "t1", 0, 0)] for sid in sg.subject_ids]
    model.Add(assignments[("1-A", "religion", "t1", 0, 0)] == 1)  # Force religion to be assigned

    # Apply the new restriction
    SubjectGroupAssignment().apply(model, assignments, all_groups, all_subjects, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
    # Now ethics should also be forced to be assigned because religion is assigned
    assert solver.Value(assignments[("1-A", "ethics", "t1", 0, 0)]) == 1
    total_assigned = sum(solver.Value(v) for v in vars_in_slot)
    assert total_assigned == 2  # Both subjects should be assigned


def test_ungrouped_subject_creates_dynamic_group_and_allows_assignment():
    """A subject without a predefined subjectgroup should be treated as a dynamic group (single member) and be assignable."""
    from restrictions import SubjectGroupAssignment

    model = cp_model.CpModel()
    all_groups = ["1-A"]

    # Subject without a subjectgroup (should create a dynamic group)
    s = TestSubject(id="math", course_id="1", weekly_hours=1, subjectgroup_id=None)
    all_subjects = [s]

    # No subjectgroups defined
    all_subjectgroups = []

    assignments = _make_vars_for_subjects(model, all_groups, all_subjects, days=1, hours=1)

    # Force the assignment to the single slot
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    SubjectGroupAssignment().apply(model, assignments, all_groups, all_subjects, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_only_one_standalone_subject_per_timeslot():
    """Only one standalone subject (not in any SubjectGroup) can be assigned per timeslot."""
    from restrictions import SubjectGroupAssignment, GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    all_groups = ["1-A"]

    # Two standalone subjects (not in any SubjectGroup)
    s1 = TestSubject(id="math", course_id="1", weekly_hours=1, subjectgroup_id=None)
    s2 = TestSubject(id="science", course_id="1", weekly_hours=1, subjectgroup_id=None)
    all_subjects = [s1, s2]

    # No subjectgroups defined
    all_subjectgroups = []

    assignments = _make_vars_for_subjects(model, all_groups, all_subjects, days=1, hours=1)

    # Try to force both standalone subjects to be assigned to the same timeslot
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "science", "t1", 0, 0)] == 1)

    # Apply both restrictions
    SubjectGroupAssignment().apply(model, assignments, all_groups, all_subjects, all_subjectgroups)
    GroupAtMostOneLogicalAssignment().apply(model, assignments, all_groups, 1, 1, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Should be infeasible because two standalone subjects cannot share a timeslot
    assert status == cp_model.INFEASIBLE


def test_subjectgroup_conflicts_with_standalone_subject():
    """A SubjectGroup and a standalone subject cannot be assigned to the same timeslot."""
    from restrictions import SubjectGroupAssignment, GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    all_groups = ["1-A"]

    # SubjectGroup with two subjects + one standalone subject
    s1 = TestSubject(id="religion", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    s2 = TestSubject(id="ethics", course_id="1", weekly_hours=1, subjectgroup_id="sg1")
    s3 = TestSubject(id="math", course_id="1", weekly_hours=1, subjectgroup_id=None)
    all_subjects = [s1, s2, s3]

    sg = TestSubjectGroup(id="sg1", subject_ids=["religion", "ethics"])
    all_subjectgroups = [sg]

    assignments = _make_vars_for_subjects(model, all_groups, all_subjects, days=1, hours=1)

    # Force SubjectGroup assignment (religion)
    model.Add(assignments[("1-A", "religion", "t1", 0, 0)] == 1)
    # Try to also assign standalone subject
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    # Apply both restrictions
    SubjectGroupAssignment().apply(model, assignments, all_groups, all_subjects, all_subjectgroups)
    GroupAtMostOneLogicalAssignment().apply(model, assignments, all_groups, 1, 1, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Should be infeasible because SubjectGroup and standalone subject conflict
    assert status == cp_model.INFEASIBLE
