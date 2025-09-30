from ortools.sat.python import cp_model
import pytest


class MockSubject:
    def __init__(self, id, course_id, weekly_hours):
        self.id = id
        self.course_id = course_id
        self.weekly_hours = weekly_hours


def test_subject_weekly_hours_basic():
    """Test that subjects are assigned their required weekly hours."""
    from restrictions import SubjectWeeklyHours

    # Setup
    model = cp_model.CpModel()
    all_groups = ["1º-A"]
    all_subjects = [
        MockSubject(id="math", course_id="1º", weekly_hours=4)
    ]

    # Create decision variables
    assignments = {}
    # Variables for one subject, one group, one teacher, over 5 days and 5 hours
    for d in range(5):
        for h in range(5):
            key = ("1º-A", "math", "teacher1", d, h)
            assignments[key] = model.NewBoolVar(f"assignment_{d}_{h}")

    # Apply restriction
    SubjectWeeklyHours().apply(model, assignments, all_groups, all_subjects)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Verify
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL

    # Count assigned hours
    total_hours = sum(solver.Value(assignments[key]) 
                     for key in assignments 
                     if key[0] == "1º-A" and key[1] == "math")
    assert total_hours == 4


def test_subject_weekly_hours_multiple_subjects():
    """Test with multiple subjects in the same course."""
    from restrictions import SubjectWeeklyHours

    # Setup
    model = cp_model.CpModel()
    all_groups = ["1º-A"]
    all_subjects = [
        MockSubject(id="math", course_id="1º", weekly_hours=4),
        MockSubject(id="science", course_id="1º", weekly_hours=3)
    ]

    # Create decision variables
    assignments = {}
    for subject in all_subjects:
        for d in range(5):
            for h in range(5):
                key = ("1º-A", subject.id, "teacher1", d, h)
                assignments[key] = model.NewBoolVar(f"assignment_{subject.id}_{d}_{h}")

    # Apply restriction
    SubjectWeeklyHours().apply(model, assignments, all_groups, all_subjects)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Verify
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL

    # Check each subject has correct hours
    for subject in all_subjects:
        total_hours = sum(solver.Value(assignments[key]) 
                         for key in assignments 
                         if key[0] == "1º-A" and key[1] == subject.id)
        assert total_hours == subject.weekly_hours


def test_subject_weekly_hours_multiple_groups():
    """Test with multiple groups in the same course."""
    from restrictions import SubjectWeeklyHours

    # Setup
    model = cp_model.CpModel()
    all_groups = ["1º-A", "1º-B"]
    all_subjects = [
        MockSubject(id="math", course_id="1º", weekly_hours=4)
    ]

    # Create decision variables
    assignments = {}
    for group in all_groups:
        for d in range(5):
            for h in range(5):
                key = (group, "math", "teacher1", d, h)
                assignments[key] = model.NewBoolVar(f"assignment_{group}_{d}_{h}")

    # Apply restriction
    SubjectWeeklyHours().apply(model, assignments, all_groups, all_subjects)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Verify
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL

    # Check each group has correct hours
    for group in all_groups:
        total_hours = sum(solver.Value(assignments[key]) 
                         for key in assignments 
                         if key[0] == group and key[1] == "math")
        assert total_hours == 4
