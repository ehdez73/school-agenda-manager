"""Tests for SubjectGroups with partial sharing (shared_hours)."""

from ortools.sat.python import cp_model
from ..schemas import TestSubject, TestSubjectGroup


def _make_assignments(model, groups, subjects, days=2, hours=3):
    assignments = {}
    for group in groups:
        for subject in subjects:
            for d in range(days):
                for h in range(hours):
                    key = (group, subject.id, "t1", d, h)
                    assignments[key] = model.NewBoolVar(f"a_{group}_{subject.id}_{d}_{h}")
    return assignments


def test_partial_sg_allows_shared_and_standalone():
    """Partial SG: COM (2h) + MUS (1h), shared_hours=1.
    COM can be at 2 slots (1 shared + 1 standalone), MUS at the shared slot only."""
    from restrictions import SubjectGroupAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    com = TestSubject(id="com", course_id="1", weekly_hours=2)
    mus = TestSubject(id="mus", course_id="1", weekly_hours=1)
    subjects = [com, mus]
    sg = TestSubjectGroup(id="sg1", subject_ids=["com", "mus"], shared_hours=1)
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, subjects, days=2, hours=3)

    # COM at (0,0) and (0,1), MUS at (0,0) only → 1 shared slot (0,0), COM standalone at (0,1)
    model.Add(assignments[("1-A", "com", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "com", "t1", 0, 1)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
        f"Expected feasible but got {status}"
    )


def test_partial_sg_enforces_exact_shared_hours():
    """shared_hours=1 means exactly 1 slot has all members active.
    Forcing 2 shared slots should be infeasible."""
    from restrictions import SubjectGroupAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    com = TestSubject(id="com", course_id="1", weekly_hours=2)
    mus = TestSubject(id="mus", course_id="1", weekly_hours=2)
    subjects = [com, mus]
    sg = TestSubjectGroup(id="sg1", subject_ids=["com", "mus"], shared_hours=1)
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, subjects, days=2, hours=3)

    # Force both at (0,0) and (0,1) → 2 shared slots → violates sum(shared)==1
    model.Add(assignments[("1-A", "com", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "com", "t1", 0, 1)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 1)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        f"Expected infeasible (2 shared slots > shared_hours=1) but got {status}"
    )


def test_partial_sg_standalone_no_conflict_with_self():
    """A member of a partial SG can be standalone at one slot
    and shared at another without conflict (GroupAtMostOneLogicalAssignment)."""
    from restrictions import SubjectGroupAssignment, GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    com = TestSubject(id="com", course_id="1", weekly_hours=2)
    mus = TestSubject(id="mus", course_id="1", weekly_hours=1)
    subjects = [com, mus]
    sg = TestSubjectGroup(id="sg1", subject_ids=["com", "mus"], shared_hours=1)
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, subjects, days=2, hours=3)

    # COM standalone at (0,0), both at (0,1) → no conflict (different slots)
    model.Add(assignments[("1-A", "com", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "com", "t1", 0, 1)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 1)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)
    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 2, 3, all_subjectgroups
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
        f"Expected feasible but got {status}"
    )


def test_partial_sg_plus_standalone_in_same_slot_infeasible():
    """A partially-shared SubjectGroup and a standalone subject
    cannot occupy the same slot (enforced by GroupAtMostOneLogicalAssignment)."""
    from restrictions import SubjectGroupAssignment, GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    com = TestSubject(id="com", course_id="1", weekly_hours=2)
    mus = TestSubject(id="mus", course_id="1", weekly_hours=1)
    math = TestSubject(id="math", course_id="1", weekly_hours=1)
    subjects = [com, mus, math]
    sg = TestSubjectGroup(id="sg1", subject_ids=["com", "mus"], shared_hours=1)
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, subjects, days=2, hours=3)

    # Full SG at (0,0) AND standalone math at (0,0) → conflict
    model.Add(assignments[("1-A", "com", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "math", "t1", 0, 0)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)
    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 2, 3, all_subjectgroups
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        f"Expected infeasible (SG + standalone in same slot) but got {status}"
    )


def test_fully_shared_sg_backward_compat():
    """When shared_hours is None, fully-shared behavior is preserved
    (all subjects must be assigned together)."""
    from restrictions import SubjectGroupAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    rel = TestSubject(id="rel", course_id="1", weekly_hours=1)
    eth = TestSubject(id="eth", course_id="1", weekly_hours=1)
    subjects = [rel, eth]
    sg = TestSubjectGroup(id="sg1", subject_ids=["rel", "eth"], shared_hours=None)
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, subjects, days=1, hours=1)

    # Force religion, verify ethics is also forced (old behavior)
    model.Add(assignments[("1-A", "rel", "t1", 0, 0)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
        f"Expected feasible but got {status}"
    )
    # Both should be active at the same slot
    assert solver.Value(assignments[("1-A", "rel", "t1", 0, 0)]) == 1
    assert solver.Value(assignments[("1-A", "eth", "t1", 0, 0)]) == 1


def test_partial_sg_standalone_only_slot():
    """A member of a partial SG can be alone at a slot where no other
    SG member is present, without triggering a shared slot count."""
    from restrictions import SubjectGroupAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    com = TestSubject(id="com", course_id="1", weekly_hours=2)
    mus = TestSubject(id="mus", course_id="1", weekly_hours=1)
    subjects = [com, mus]
    sg = TestSubjectGroup(id="sg1", subject_ids=["com", "mus"], shared_hours=1)
    all_subjectgroups = [sg]

    assignments = _make_assignments(model, groups, subjects, days=2, hours=3)

    # COM at (0,0) alone (standalone), MUS at (0,1) alone
    # COM at (0,2) + MUS at (0,2) → shared (counts toward shared_hours=1)
    model.Add(assignments[("1-A", "com", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 1)] == 1)
    model.Add(assignments[("1-A", "com", "t1", 0, 2)] == 1)
    model.Add(assignments[("1-A", "mus", "t1", 0, 2)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
        f"Expected feasible but got {status}"
    )


def test_partial_sg_three_members_missing_one_at_slot():
    """With 3 SG members, a slot counts as shared only when ALL are active.
    A missing member means the slot cannot be shared (shared_hours=1 → infeasible)."""
    from restrictions import SubjectGroupAssignment, GroupAtMostOneLogicalAssignment

    model = cp_model.CpModel()
    groups = ["1-A"]
    a = TestSubject(id="subj_a", course_id="1", weekly_hours=2)
    b = TestSubject(id="subj_b", course_id="1", weekly_hours=2)
    c = TestSubject(id="subj_c", course_id="1", weekly_hours=2)
    subjects = [a, b, c]
    sg = TestSubjectGroup(id="sg1", subject_ids=["subj_a", "subj_b", "subj_c"], shared_hours=1)
    all_subjectgroups = [sg]

    assignments = {}
    for d in range(2):
        for h in range(3):
            assignments[("1-A", "subj_a", "t1", d, h)] = model.NewBoolVar(f"a_{d}_{h}")
            assignments[("1-A", "subj_b", "t1", d, h)] = model.NewBoolVar(f"b_{d}_{h}")
            if d != 0 or h != 0:
                assignments[("1-A", "subj_c", "t1", d, h)] = model.NewBoolVar(f"c_{d}_{h}")

    model.Add(assignments[("1-A", "subj_a", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "subj_b", "t1", 0, 0)] == 1)

    SubjectGroupAssignment().apply(model, assignments, groups, subjects, all_subjectgroups)
    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, groups, 2, 3, all_subjectgroups
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE, (
        f"Expected infeasible (no slot can be shared, shared_hours=1) but got {status}"
    )
