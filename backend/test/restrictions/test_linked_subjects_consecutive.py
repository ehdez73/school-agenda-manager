"""Unit tests for the LinkedSubjectsConsecutive restriction.

We construct a small CpModel with two subjects linked together and assert that scheduling
both on the same day in non-consecutive hours is infeasible while consecutive hours
are allowed.
"""

from ortools.sat.python import cp_model
from backend.restrictions.linked_subjects_consecutive import LinkedSubjectsConsecutive


class DummySubject:
    def __init__(self, id, course_id, linked_subject_id=None):
        self.id = id
        self.course_id = course_id
        self.linked_subject_id = linked_subject_id


def test_linked_subjects_forbid_non_consecutive():
    model = cp_model.CpModel()

    groups = ["1-A"]
    num_days = 1
    num_hours = 5

    # two subjects in same course, subject a links to b
    a = DummySubject("A", "1", linked_subject_id="B")
    b = DummySubject("B", "1")
    subjects = [a, b]

    # create assignments dict like scheduler does: (group, subject_id, teacher_id, d, h)
    assignments = {}
    # single dummy teacher id 1
    for d in range(num_days):
        for h in range(num_hours):
            assignments[("1-A", "A", 1, d, h)] = model.NewBoolVar(f"A_d{d}_h{h}")
            assignments[("1-A", "B", 1, d, h)] = model.NewBoolVar(f"B_d{d}_h{h}")

    # apply restriction
    LinkedSubjectsConsecutive().apply(
        model, assignments, groups, subjects, num_days, num_hours
    )

    # Force A at hour 0 and B at hour 3 (non-consecutive)
    model.Add(assignments[("1-A", "A", 1, 0, 0)] == 1)
    model.Add(assignments[("1-A", "B", 1, 0, 3)] == 1)

    # In the real scheduler the weekly-hours restriction prevents adding
    # extra occurrences to satisfy adjacency. Simulate that here by forcing
    # each subject to appear exactly once on the day.
    model.Add(
        sum(assignments[("1-A", "A", 1, 0, h)] for h in range(num_hours)) == 1
    )
    model.Add(
        sum(assignments[("1-A", "B", 1, 0, h)] for h in range(num_hours)) == 1
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE or status == cp_model.MODEL_INVALID


def test_linked_subjects_allow_consecutive():
    model = cp_model.CpModel()

    groups = ["1-A"]
    num_days = 1
    num_hours = 5

    a = DummySubject("A", "1", linked_subject_id="B")
    b = DummySubject("B", "1")
    subjects = [a, b]

    assignments = {}
    for d in range(num_days):
        for h in range(num_hours):
            assignments[("1-A", "A", 1, d, h)] = model.NewBoolVar(f"A_d{d}_h{h}")
            assignments[("1-A", "B", 1, d, h)] = model.NewBoolVar(f"B_d{d}_h{h}")

    LinkedSubjectsConsecutive().apply(
        model, assignments, groups, subjects, num_days, num_hours
    )

    # Force A at hour 1 and B at hour 2 (consecutive)
    model.Add(assignments[("1-A", "A", 1, 0, 1)] == 1)
    model.Add(assignments[("1-A", "B", 1, 0, 2)] == 1)

    # Simulate weekly-hours: each subject appears exactly once
    model.Add(
        sum(assignments[("1-A", "A", 1, 0, h)] for h in range(num_hours)) == 1
    )
    model.Add(
        sum(assignments[("1-A", "B", 1, 0, h)] for h in range(num_hours)) == 1
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE
