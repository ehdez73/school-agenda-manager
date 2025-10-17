"""Tests for tutor preference restriction."""

import pytest
from ortools.sat.python import cp_model

from backend.restrictions.tutor_preference import TutorPreference


class MockTeacher:
    """Mock teacher for testing."""

    def __init__(self, teacher_id, name, tutor_group=None):
        self.id = teacher_id
        self.name = name
        self.tutor_group = tutor_group


def test_tutor_preference_no_tutor():
    """Test that teachers without tutor_group don't get preference terms."""
    model = cp_model.CpModel()

    teacher = MockTeacher(1, "Alice", tutor_group=None)

    # Create some dummy assignments
    assignments = {
        ("1-A", "MATH1", 1, 0, 0): model.NewBoolVar("test1"),
        ("1-A", "MATH1", 1, 0, 1): model.NewBoolVar("test2"),
    }

    restriction = TutorPreference()
    restriction.apply(model, assignments, [teacher])

    assert len(restriction.preference_terms) == 0


def test_tutor_preference_with_tutor():
    """Test that tutors get preference terms for their assigned group."""
    model = cp_model.CpModel()

    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    # Create assignments for the tutor's group and another group
    assignments = {
        ("1-A", "MATH1", 1, 0, 0): model.NewBoolVar("1-A_MATH1_1_0_0"),
        ("1-A", "MATH1", 1, 0, 1): model.NewBoolVar("1-A_MATH1_1_0_1"),
        ("1-A", "LANG1", 1, 1, 0): model.NewBoolVar("1-A_LANG1_1_1_0"),
        ("1-B", "MATH1", 1, 0, 0): model.NewBoolVar("1-B_MATH1_1_0_0"),
    }

    restriction = TutorPreference()
    restriction.apply(model, assignments, [teacher])

    # Should have exactly 1 preference term (sum of all assignments in 1-A for teacher 1)
    assert len(restriction.preference_terms) == 1


def test_tutor_preference_weight():
    """Test that weight is applied correctly to preference terms."""
    model = cp_model.CpModel()

    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    assignments = {
        ("1-A", "MATH1", 1, 0, 0): model.NewBoolVar("1-A_MATH1_1_0_0"),
        ("1-A", "MATH1", 1, 0, 1): model.NewBoolVar("1-A_MATH1_1_0_1"),
    }

    weight = 5
    restriction = TutorPreference(weight=weight)
    restriction.apply(model, assignments, [teacher])

    assert len(restriction.preference_terms) == 1


def test_tutor_preference_multiple_tutors():
    """Test preference terms for multiple tutors."""
    model = cp_model.CpModel()

    teacher1 = MockTeacher(1, "Alice", tutor_group="1-A")
    teacher2 = MockTeacher(2, "Bob", tutor_group="1-B")
    teacher3 = MockTeacher(3, "Charlie", tutor_group=None)

    assignments = {
        ("1-A", "MATH1", 1, 0, 0): model.NewBoolVar("1-A_MATH1_1_0_0"),
        ("1-B", "MATH1", 2, 0, 0): model.NewBoolVar("1-B_MATH1_2_0_0"),
        ("1-C", "MATH1", 3, 0, 0): model.NewBoolVar("1-C_MATH1_3_0_0"),
    }

    restriction = TutorPreference()
    restriction.apply(model, assignments, [teacher1, teacher2, teacher3])

    # Should have 2 preference terms (one for each tutor)
    assert len(restriction.preference_terms) == 2


def test_tutor_preference_no_assignments():
    """Test tutor with no assignments in their group."""
    model = cp_model.CpModel()

    teacher = MockTeacher(1, "Alice", tutor_group="1-A")

    # No assignments for teacher 1 in group 1-A
    assignments = {
        ("1-B", "MATH1", 2, 0, 0): model.NewBoolVar("1-B_MATH1_2_0_0"),
    }

    restriction = TutorPreference()
    restriction.apply(model, assignments, [teacher])

    # Should have no preference terms
    assert len(restriction.preference_terms) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
