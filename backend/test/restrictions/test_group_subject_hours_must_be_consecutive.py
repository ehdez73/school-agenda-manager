from ortools.sat.python import cp_model
import logging

logger = logging.getLogger(__name__)


def status_name(status):
    names = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }
    return names.get(status, f"STATUS_{status}")


def test_group_subject_hours_must_be_consecutive_allows_consecutive():
    from restrictions import GroupSubjectHoursMustBeConsecutive

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 3

    class MockSubject:
        def __init__(self, id, course_id):
            self.id = id
            self.course_id = course_id

    subject = MockSubject(id="s1", course_id="1")
    groups = ["1-A"]
    subjects = [subject]

    assignments = {}
    # consecutive hours 0 and 1
    assignments[("1-A", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("1-A", "s1", "t1", 0, 1)] = model.NewBoolVar("a1")
    assignments[("1-A", "s1", "t1", 0, 2)] = model.NewBoolVar("a2")

    # Force hours 0 and 1 to be set
    model.Add(assignments[("1-A", "s1", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "s1", "t1", 0, 1)] == 1)

    GroupSubjectHoursMustBeConsecutive().apply(model, assignments, groups, subjects, num_days, num_hours)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_group_subject_hours_must_be_consecutive_blocks_non_consecutive():
    from restrictions import GroupSubjectHoursMustBeConsecutive

    model = cp_model.CpModel()
    num_days = 1
    num_hours = 3

    class MockSubject:
        def __init__(self, id, course_id):
            self.id = id
            self.course_id = course_id

    subject = MockSubject(id="s1", course_id="1")
    groups = ["1-A"]
    subjects = [subject]

    assignments = {}
    # non-consecutive hours 0 and 2
    assignments[("1-A", "s1", "t1", 0, 0)] = model.NewBoolVar("a0")
    assignments[("1-A", "s1", "t1", 0, 1)] = model.NewBoolVar("a1")
    assignments[("1-A", "s1", "t1", 0, 2)] = model.NewBoolVar("a2")

    # Force hours 0 and 2 to be set
    model.Add(assignments[("1-A", "s1", "t1", 0, 0)] == 1)
    model.Add(assignments[("1-A", "s1", "t1", 0, 1)] == 0)
    model.Add(assignments[("1-A", "s1", "t1", 0, 2)] == 1)

    GroupSubjectHoursMustBeConsecutive().apply(model, assignments, groups, subjects, num_days, num_hours)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    logger.info("Solver status: %s", status_name(status))
    assert status == cp_model.INFEASIBLE
