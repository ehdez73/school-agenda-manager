"""Tests for teacher_subject_lines filtering in _create_assignments."""
from ortools.sat.python import cp_model
from backend.scheduler import _create_assignments


class MockTeacher:
    def __init__(self, id, name, subjects=None):
        self.id = id
        self.name = name
        self.subjects = subjects or []


class MockSubject:
    def __init__(self, id, name, course_id, included_lines=None, weekly_hours=2):
        self.id = id
        self.name = name
        self.course_id = course_id
        self.included_lines = included_lines
        self.weekly_hours = weekly_hours


def test_no_teacher_subject_lines_creates_all_assignments():
    model = cp_model.CpModel()
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1")
    teacher = MockTeacher(id=1, name="Luis", subjects=[subj])
    groups = ["1-A", "1-B"]

    assignments = _create_assignments(
        model, [teacher], [subj], groups, num_days=2, num_hours=2,
    )

    # Both lines should have assignments for (LEN1, Luis)
    keys_a = [k for k in assignments if k[0] == "1-A"]
    keys_b = [k for k in assignments if k[0] == "1-B"]
    assert len(keys_a) == 4  # 2 days * 2 hours
    assert len(keys_b) == 4


def test_teacher_subject_lines_filters_out_excluded_lines():
    model = cp_model.CpModel()
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1")
    teacher = MockTeacher(id=1, name="Luis", subjects=[subj])
    groups = ["1-A", "1-B"]

    teacher_subject_lines = {(1, "LEN1"): [0]}  # only line A (index 0)
    assignments = _create_assignments(
        model, [teacher], [subj], groups, num_days=2, num_hours=2,
        teacher_subject_lines=teacher_subject_lines,
    )

    keys_a = [k for k in assignments if k[0] == "1-A"]
    keys_b = [k for k in assignments if k[0] == "1-B"]
    assert len(keys_a) == 4
    assert len(keys_b) == 0  # line B excluded


def test_teacher_subject_lines_allows_multiple_lines():
    model = cp_model.CpModel()
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1")
    teacher = MockTeacher(id=1, name="Luis", subjects=[subj])
    groups = ["1-A", "1-B", "1-C"]

    teacher_subject_lines = {(1, "LEN1"): [0, 2]}  # lines A and C
    assignments = _create_assignments(
        model, [teacher], [subj], groups, num_days=2, num_hours=2,
        teacher_subject_lines=teacher_subject_lines,
    )

    keys_a = [k for k in assignments if k[0] == "1-A"]
    keys_b = [k for k in assignments if k[0] == "1-B"]
    keys_c = [k for k in assignments if k[0] == "1-C"]
    assert len(keys_a) == 4
    assert len(keys_b) == 0  # excluded
    assert len(keys_c) == 4


def test_teacher_subject_lines_per_teacher_subject_pair():
    model = cp_model.CpModel()
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1")
    teacher1 = MockTeacher(id=1, name="Luis", subjects=[subj])
    teacher2 = MockTeacher(id=2, name="Ana", subjects=[subj])
    groups = ["1-A", "1-B"]

    teacher_subject_lines = {
        (1, "LEN1"): [0],  # Luis only line A
        (2, "LEN1"): [1],  # Ana only line B
    }
    assignments = _create_assignments(
        model, [teacher1, teacher2], [subj], groups, num_days=1, num_hours=1,
        teacher_subject_lines=teacher_subject_lines,
    )

    luis_a = [k for k in assignments if k[0] == "1-A" and k[2] == 1]
    luis_b = [k for k in assignments if k[0] == "1-B" and k[2] == 1]
    ana_a = [k for k in assignments if k[0] == "1-A" and k[2] == 2]
    ana_b = [k for k in assignments if k[0] == "1-B" and k[2] == 2]
    assert len(luis_a) == 1
    assert len(luis_b) == 0
    assert len(ana_a) == 0
    assert len(ana_b) == 1


def test_teacher_subject_lines_and_subject_included_lines_are_and():
    model = cp_model.CpModel()
    # Subject is only for line A (included_lines=[0])
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1", included_lines=[0])
    teacher = MockTeacher(id=1, name="Luis", subjects=[subj])
    groups = ["1-A", "1-B"]

    # Teacher-subject lines say only line B — but subject is only for line A
    teacher_subject_lines = {(1, "LEN1"): [1]}
    assignments = _create_assignments(
        model, [teacher], [subj], groups, num_days=1, num_hours=1,
        teacher_subject_lines=teacher_subject_lines,
    )

    # No assignments because Subject says line A only, teacher-subject says line B only
    assert len(assignments) == 0


def test_teacher_subject_lines_none_defaults_to_all_lines():
    model = cp_model.CpModel()
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1")
    teacher = MockTeacher(id=1, name="Luis", subjects=[subj])
    groups = ["1-A", "1-B"]

    # teacher_subject_lines with None value = all lines
    teacher_subject_lines = {(1, "LEN1"): None}
    assignments = _create_assignments(
        model, [teacher], [subj], groups, num_days=2, num_hours=2,
        teacher_subject_lines=teacher_subject_lines,
    )

    keys_a = [k for k in assignments if k[0] == "1-A"]
    keys_b = [k for k in assignments if k[0] == "1-B"]
    assert len(keys_a) == 4
    assert len(keys_b) == 4


def test_teacher_subject_lines_not_in_dict_defaults_to_all_lines():
    model = cp_model.CpModel()
    subj = MockSubject(id="LEN1", name="Lengua", course_id="1")
    teacher = MockTeacher(id=1, name="Luis", subjects=[subj])
    groups = ["1-A", "1-B"]

    # Luis is not in the dict at all — should default to all lines
    teacher_subject_lines = {(99, "OTHER"): [0]}
    assignments = _create_assignments(
        model, [teacher], [subj], groups, num_days=2, num_hours=2,
        teacher_subject_lines=teacher_subject_lines,
    )

    keys_a = [k for k in assignments if k[0] == "1-A"]
    keys_b = [k for k in assignments if k[0] == "1-B"]
    assert len(keys_a) == 4
    assert len(keys_b) == 4
