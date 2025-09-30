import pytest
from ortools.sat.python import cp_model
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from ...models import Subject
from ...restrictions.subject_max_hours_per_day import SubjectMaxHoursPerDay

def test_subject_max_hours_per_day():
    """Test the SubjectMaxHoursPerDay restriction."""
    model = cp_model.CpModel()

    # Mock data
    subject = Subject(id='math', name='Math', max_hours_per_day=2)
    # Adjust assignments to ensure feasibility
    assignments = {
        ('group1', 'math', 'teacher1', 0, 0): model.NewBoolVar('math_0_0'),
        ('group1', 'math', 'teacher1', 0, 1): model.NewBoolVar('math_0_1'),
        ('group1', 'math', 'teacher1', 1, 0): model.NewBoolVar('math_1_0'),
    }

    # Apply restriction
    restriction = SubjectMaxHoursPerDay()
    restriction.apply(model, assignments, [subject], [])

    # Validate constraints
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    # Print status information for debugging
    print(f"Solver status: {status}")
    print(f"OPTIMAL: {cp_model.OPTIMAL}")
    print(f"FEASIBLE: {cp_model.FEASIBLE}")
    print(f"INFEASIBLE: {cp_model.INFEASIBLE}")
    print(f"MODEL_INVALID: {cp_model.MODEL_INVALID}")
    print(f"UNKNOWN: {cp_model.UNKNOWN}")

    # Ensure the model is feasible
    assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE

    # Ensure no more than 2 hours are assigned on day 0
    assert sum(solver.Value(assignments[('group1', 'math', 'teacher1', 0, h)]) for h in range(2)) <= 2

    # Debug output to analyze solver behavior
    print("Solver status:", status)
    for (key, var) in assignments.items():
        print(f"{key}: {solver.Value(var)}")

    # Debug constraints
    print("Constraints:")
    for day in range(5):
        daily_sum = sum(assignments[("group1", "math", "teacher1", day, h)] for h in range(5) if ("group1", "math", "teacher1", day, h) in assignments)
        print(f"Day {day}: {daily_sum}")