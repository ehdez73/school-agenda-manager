from ortools.sat.python import cp_model


class MockTeacher:
    def __init__(self, id):
        self.id = id


class MockSubject:
    def __init__(self, id, course_id, weekly_hours=1):
        self.id = id
        self.course_id = course_id
        self.weekly_hours = weekly_hours


def test_teacher_one_subject_per_group_allows_one_teacher():
    from backend.restrictions.teacher_one_subject_per_group import (
        TeacherOneSubjectPerGroup,
    )

    model = cp_model.CpModel()

    teachers = [MockTeacher(id="t1")]
    groups = ["1-A"]
    subjects = [MockSubject(id="math", course_id="1", weekly_hours=2)]

    assignments = {}
    for d in range(2):
        for h in range(2):
            assignments[("1-A", "math", "t1", d, h)] = model.NewBoolVar(
                f"a_{d}_{h}")

    TeacherOneSubjectPerGroup().apply(model, assignments, teachers, groups, subjects)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL


def test_teacher_one_subject_per_group_blocks_two_teachers():
    from backend.restrictions.teacher_one_subject_per_group import (
        TeacherOneSubjectPerGroup,
    )

    model = cp_model.CpModel()

    teachers = [MockTeacher(id="t1"), MockTeacher(id="t2")]
    groups = ["1-A"]
    subjects = [MockSubject(id="math", course_id="1", weekly_hours=2)]

    assignments = {}
    for teacher in teachers:
        for d in range(2):
            for h in range(2):
                assignments[("1-A", "math", teacher.id, d, h)] = model.NewBoolVar(
                    f"a_{teacher.id}_{d}_{h}")

    TeacherOneSubjectPerGroup().apply(model, assignments, teachers, groups, subjects)

    # Force both teachers to have at least one hour — violation
    model.Add(sum(
        assignments[("1-A", "math", "t1", d, h)] for d in range(2) for h in range(2)
    ) >= 1)
    model.Add(sum(
        assignments[("1-A", "math", "t2", d, h)] for d in range(2) for h in range(2)
    ) >= 1)
    # Also need enough total hours to satisfy at-most-one active teacher
    model.Add(sum(assignments.values()) <= 2)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.INFEASIBLE


def test_teacher_one_subject_ignores_other_courses():
    from backend.restrictions.teacher_one_subject_per_group import (
        TeacherOneSubjectPerGroup,
    )

    model = cp_model.CpModel()

    teachers = [MockTeacher(id="t1"), MockTeacher(id="t2")]
    groups = ["1-A", "2-A"]
    subjects = [MockSubject(id="math", course_id="1", weekly_hours=2)]

    # Both teachers assigned to group "2-A" which is course "2" — subject is course "1",
    # so restriction shouldn't fire (course_id mismatch).
    assignments = {}
    for teacher in teachers:
        key = ("2-A", "math", teacher.id, 0, 0)
        assignments[key] = model.NewBoolVar(f"a_{teacher.id}")

    model.Add(assignments[("2-A", "math", "t1", 0, 0)] == 1)
    model.Add(assignments[("2-A", "math", "t2", 0, 0)] == 1)

    TeacherOneSubjectPerGroup().apply(model, assignments, teachers, groups, subjects)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert status == cp_model.FEASIBLE or status == cp_model.OPTIMAL
