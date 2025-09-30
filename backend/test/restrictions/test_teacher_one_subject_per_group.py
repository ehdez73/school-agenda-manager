import pytest
from ortools.sat.python import cp_model
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from ...restrictions.teacher_one_subject_per_group import TeacherOneSubjectPerGroup

class MockTeacher:
    def __init__(self, id):
        self.id = id

class MockSubject:
    def __init__(self, id):
        self.id = id

def test_teacher_one_subject_per_group():
    """Test the TeacherOneSubjectPerGroup restriction."""
    model = cp_model.CpModel()

    # Mock data
    teachers = [MockTeacher(id="t1"), MockTeacher(id="t2")]
    groups = ["1A"]
    subjects = [MockSubject(id="math")]

    # Create decision variables
    assignments = {}
    for teacher in teachers:
        for day in range(5):
            for hour in range(5):
                key = ("1A", "math", teacher.id, day, hour)
                assignments[key] = model.NewBoolVar(f"assignment_{teacher.id}_{day}_{hour}")

    # Apply restriction
    TeacherOneSubjectPerGroup().apply(model, assignments, teachers, groups, subjects)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Verify
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
    for day in range(5):
        for hour in range(5):
            assert sum(
                solver.Value(assignments[("1A", "math", teacher.id, day, hour)])
                for teacher in teachers
            ) <= 1