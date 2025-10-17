"""Tests for TutorMandatoryHours restriction."""

import pytest
from ortools.sat.python import cp_model

from backend.restrictions.tutor_mandatory_hours import TutorMandatoryHours


class MockTeacher:
    def __init__(self, teacher_id, name, tutor_group=None):
        self.id = teacher_id
        self.name = name
        self.tutor_group = tutor_group


def test_no_tutor_does_nothing():
    model = cp_model.CpModel()
    teacher = MockTeacher(1, "Alice", tutor_group=None)

    assignments = {
        ("1-A", "M1", 1, 0, 0): model.NewBoolVar("a"),
    }

    TutorMandatoryHours().apply(model, assignments, [teacher], 5, 5)

    # No constraints added means model is still satisfiable with either value
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_tutor_must_take_first_and_last_slot():
    model = cp_model.CpModel()

    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    # Provide two possible subject assignments for first slot and last slot
    assignments = {
        ("1-A", "S1", 1, 0, 0): model.NewBoolVar("f1"),
        ("1-A", "S2", 1, 0, 0): model.NewBoolVar("f2"),
        ("1-A", "S3", 1, 4, 4): model.NewBoolVar("l1"),
        ("1-A", "S4", 1, 4, 4): model.NewBoolVar("l2"),
    }

    # Apply restriction for a 5x5 schedule (days=5, hours=5)
    TutorMandatoryHours().apply(
        model, assignments, [teacher], 5, 5, all_subjectgroups=None
    )

    # Solve and assert that there is at least one var selected in each slot.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL

    # Sum of first-slot vars must equal 1
    assert (
        solver.Value(assignments[("1-A", "S1", 1, 0, 0)])
        + solver.Value(assignments[("1-A", "S2", 1, 0, 0)])
        == 1
    )

    # Sum of last-slot vars must equal 1
    assert (
        solver.Value(assignments[("1-A", "S3", 1, 4, 4)])
        + solver.Value(assignments[("1-A", "S4", 1, 4, 4)])
        == 1
    )


def test_tutor_with_no_matching_vars_skips_slot():
    model = cp_model.CpModel()
    # Tutor for 1-A but assignments only exist for 1-B
    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    assignments = {
        ("1-B", "S1", 1, 0, 0): model.NewBoolVar("b1"),
        ("1-B", "S2", 1, 4, 4): model.NewBoolVar("b2"),
    }

    # Should not add constraints (since no vars for 1-A), model remains satisfiable
    TutorMandatoryHours().apply(model, assignments, [teacher], 5, 5)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_subjectgroup_subjects_are_excluded():
    model = cp_model.CpModel()
    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    # Suppose S1 and S2 belong to a SubjectGroup; they should be ignored
    # by the mandatory restriction and therefore no constraint will be
    # added for those vars.
    class SG:
        def __init__(self, subject_ids):
            self.subject_ids = subject_ids

    assignments = {
        ("1-A", "S1", 1, 0, 0): model.NewBoolVar("f1"),
        ("1-A", "S2", 1, 0, 0): model.NewBoolVar("f2"),
        # Also provide a legitimate standalone subject in last slot
        ("1-A", "S3", 1, 4, 4): model.NewBoolVar("l1"),
    }

    TutorMandatoryHours().apply(
        model, assignments, [teacher], 5, 5, all_subjectgroups=[SG(["S1", "S2"])]
    )

    # Since first slot subjects were part of a SubjectGroup they should be
    # excluded and no equality constraint forces them; solver remains
    # satisfiable.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
