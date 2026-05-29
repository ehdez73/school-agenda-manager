"""Tests for TutorMandatoryHours restriction."""

import pytest
from ortools.sat.python import cp_model

from backend.restrictions.tutor_mandatory_hours import TutorMandatoryHours


class MockTeacher:
    def __init__(self, teacher_id, name, tutor_group=None, tutor_groups=None):
        self.id = teacher_id
        self.name = name
        self.tutor_group = tutor_group
        self.tutor_groups = tutor_groups


def test_no_tutor_does_nothing():
    model = cp_model.CpModel()
    teacher = MockTeacher(1, "Alice", tutor_group=None)

    assignments = {
        ("1-A", "M1", 1, 0, 0): model.NewBoolVar("a"),
    }

    r = TutorMandatoryHours()
    r.apply(model, assignments, [teacher], 5, 5)

    # No preference terms added when teacher has no tutor group
    assert r.preference_terms == []


def test_tutor_rewarded_for_first_and_last_slot():
    model = cp_model.CpModel()

    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    assignments = {
        ("1-A", "S1", 1, 0, 0): model.NewBoolVar("f1"),
        ("1-A", "S2", 1, 0, 0): model.NewBoolVar("f2"),
        ("1-A", "S3", 1, 4, 4): model.NewBoolVar("l1"),
        ("1-A", "S4", 1, 4, 4): model.NewBoolVar("l2"),
    }

    r = TutorMandatoryHours(weight=500)
    r.apply(model, assignments, [teacher], 5, 5, all_subjectgroups=None)

    # Preference terms should be added for first and last slot
    assert len(r.preference_terms) == 2

    # Simulate real constraints: at most one subject per teacher per slot
    model.AddAtMostOne(assignments[("1-A", "S1", 1, 0, 0)],
                       assignments[("1-A", "S2", 1, 0, 0)])
    model.AddAtMostOne(assignments[("1-A", "S3", 1, 4, 4)],
                       assignments[("1-A", "S4", 1, 4, 4)])

    model.Maximize(sum(r.preference_terms))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status in (cp_model.FEASIBLE, cp_model.OPTIMAL)

    # With maximization and no conflicting constraints, the tutor should
    # be assigned to both mandatory slots
    assert (
        solver.Value(assignments[("1-A", "S1", 1, 0, 0)])
        + solver.Value(assignments[("1-A", "S2", 1, 0, 0)])
        == 1
    )
    assert (
        solver.Value(assignments[("1-A", "S3", 1, 4, 4)])
        + solver.Value(assignments[("1-A", "S4", 1, 4, 4)])
        == 1
    )


def test_tutor_with_no_matching_vars_skips_slot():
    model = cp_model.CpModel()
    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    assignments = {
        ("1-B", "S1", 1, 0, 0): model.NewBoolVar("b1"),
        ("1-B", "S2", 1, 4, 4): model.NewBoolVar("b2"),
    }

    r = TutorMandatoryHours()
    r.apply(model, assignments, [teacher], 5, 5)

    # No preference terms for a group that has no matching assignments
    assert r.preference_terms == []


def test_subjectgroup_subjects_are_excluded():
    model = cp_model.CpModel()
    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    class SG:
        def __init__(self, subject_ids):
            self.subject_ids = subject_ids

    assignments = {
        ("1-A", "S1", 1, 0, 0): model.NewBoolVar("f1"),
        ("1-A", "S2", 1, 0, 0): model.NewBoolVar("f2"),
        ("1-A", "S3", 1, 4, 4): model.NewBoolVar("l1"),
    }

    r = TutorMandatoryHours()
    r.apply(
        model, assignments, [teacher], 5, 5, all_subjectgroups=[SG(["S1", "S2"])]
    )

    # First slot subjects are excluded (belong to SubjectGroup), so only
    # the last slot gets a preference term
    assert len(r.preference_terms) == 1


def test_multiple_tutor_groups_add_multiple_terms():
    model = cp_model.CpModel()
    teacher = MockTeacher(1, "Alice", tutor_groups=["1-A", "1-B"])

    assignments = {
        ("1-A", "S1", 1, 0, 0): model.NewBoolVar("a1"),
        ("1-A", "S2", 1, 4, 4): model.NewBoolVar("a2"),
        ("1-B", "S1", 1, 0, 0): model.NewBoolVar("b1"),
        ("1-B", "S2", 1, 4, 4): model.NewBoolVar("b2"),
    }

    r = TutorMandatoryHours()
    r.apply(model, assignments, [teacher], 5, 5)

    assert len(r.preference_terms) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
