"""Tests for the infeasibility diagnostic pre-checks (Phase 1 sanity checks)."""

from backend.scheduler import (
    _check_subjectgroup_weekly_hours_consistency,
    _check_teacher_capacity_vs_load,
    _check_teach_every_day_viability,
    diagnose_infeasibility,
)


class MockTeacher:
    def __init__(self, id, name, max_hours_week=10, subjects=None,
                 tutor_group=None, preferences=None):
        self.id = id
        self.name = name
        self.max_hours_week = max_hours_week
        self.subjects = subjects or []
        self.tutor_group = tutor_group
        self.preferences = preferences


class MockSubject:
    def __init__(self, id, name, course_id, weekly_hours=1,
                 max_hours_per_day=1, teach_every_day=False):
        self.id = id
        self.name = name
        self.course_id = course_id
        self.weekly_hours = weekly_hours
        self.max_hours_per_day = max_hours_per_day
        self.consecutive_hours = True
        self.teach_every_day = teach_every_day
        self.linked_subject_id = None


class MockSubjectGroup:
    def __init__(self, subjects=None, name=None):
        self.subjects = subjects or []
        self.name = name
        self.id = id(subjects)


# ---------------------------------------------------------------------------
# _check_subjectgroup_weekly_hours_consistency
# ---------------------------------------------------------------------------

def test_subjectgroup_weekly_hours_all_same():
    sg = MockSubjectGroup([
        MockSubject("A1", "Math", "1", weekly_hours=4),
        MockSubject("A2", "Music", "1", weekly_hours=4),
    ], name="MATH-MUSIC")
    assert _check_subjectgroup_weekly_hours_consistency([sg]) == []


def test_subjectgroup_weekly_hours_different():
    sg = MockSubjectGroup([
        MockSubject("A1", "Math", "1", weekly_hours=4),
        MockSubject("A2", "Music", "1", weekly_hours=2),
    ], name="MATH-MUSIC")
    issues = _check_subjectgroup_weekly_hours_consistency([sg])
    assert len(issues) == 1
    assert "SubjectGroup" in issues[0]
    assert "different weekly_hours" in issues[0]


def test_subjectgroup_weekly_hours_single_subject():
    sg = MockSubjectGroup([
        MockSubject("A1", "Math", "1", weekly_hours=3),
    ], name="MATH-ONLY")
    assert _check_subjectgroup_weekly_hours_consistency([sg]) == []


def test_subjectgroup_weekly_hours_empty():
    assert _check_subjectgroup_weekly_hours_consistency([]) == []


# ---------------------------------------------------------------------------
# _check_teacher_capacity_vs_load
# ---------------------------------------------------------------------------

def test_teacher_capacity_sufficient():
    t = MockTeacher(1, "Ana", max_hours_week=10,
                    subjects=[MockSubject("M1", "Math", "1", weekly_hours=5)])
    subjects = [MockSubject("M1", "Math", "1", weekly_hours=5)]
    assert _check_teacher_capacity_vs_load([t], subjects, ["1-A"], []) == []


def test_teacher_capacity_insufficient():
    t = MockTeacher(1, "Ana", max_hours_week=4,
                    subjects=[MockSubject("M1", "Math", "1", weekly_hours=5)])
    subjects = [MockSubject("M1", "Math", "1", weekly_hours=5)]
    issues = _check_teacher_capacity_vs_load([t], subjects, ["1-A"], [])
    assert len(issues) >= 1
    assert any("max_hours_week" in i and "Ana" in i for i in issues)


def test_teacher_capacity_global_insufficient():
    t1 = MockTeacher(1, "Ana", max_hours_week=4,
                     subjects=[MockSubject("M1", "Math", "1", weekly_hours=5)])
    t2 = MockTeacher(2, "Luis", max_hours_week=4,
                     subjects=[MockSubject("L1", "Lang", "1", weekly_hours=8)])
    subjects = [
        MockSubject("M1", "Math", "1", weekly_hours=5),
        MockSubject("L1", "Lang", "1", weekly_hours=8),
    ]
    issues = _check_teacher_capacity_vs_load([t1, t2], subjects, ["1-A"], [])
    assert any("Global capacity" in i or "exceed total" in i for i in issues)


# ---------------------------------------------------------------------------
# _check_teach_every_day_viability
# ---------------------------------------------------------------------------

def test_teach_every_day_feasible():
    s = MockSubject("M1", "Math", "1", weekly_hours=5,
                    max_hours_per_day=1, teach_every_day=True)
    assert _check_teach_every_day_viability([s], ["1-A"], 5) == []


def test_teach_every_day_too_few_hours():
    s = MockSubject("M1", "Math", "1", weekly_hours=2,
                    max_hours_per_day=1, teach_every_day=True)
    issues = _check_teach_every_day_viability([s], ["1-A"], 5)
    assert len(issues) == 1
    assert "teach_every_day" in issues[0]
    assert "2h/week" in issues[0]


def test_teach_every_day_exceeds_max_per_day():
    s = MockSubject("M1", "Math", "1", weekly_hours=6,
                    max_hours_per_day=1, teach_every_day=True)
    issues = _check_teach_every_day_viability([s], ["1-A"], 5)
    assert len(issues) >= 1
    assert any("max_hours_per_day" in i for i in issues)


# ---------------------------------------------------------------------------
# diagnose_infeasibility — integration
# ---------------------------------------------------------------------------

def test_diagnose_infeasibility_no_issues():
    t = MockTeacher(1, "Ana", max_hours_week=10,
                    subjects=[MockSubject("M1", "Math", "1", weekly_hours=3)])
    subjects = [MockSubject("M1", "Math", "1", weekly_hours=3)]
    result = diagnose_infeasibility([t], subjects, ["1-A"], [], 5, 5)
    assert result["sanity_issues"] == []
    assert "suspects" in result
    assert "entity_conflicts" in result


def test_diagnose_infeasibility_precheck_fails():
    result = diagnose_infeasibility(
        [], [], ["1-A"],
        [MockSubjectGroup([
            MockSubject("A1", "Math", "1", weekly_hours=4),
            MockSubject("A2", "Music", "1", weekly_hours=2),
        ], name="MATH-MUSIC")],
        5, 5,
    )
    assert len(result["sanity_issues"]) >= 1
    assert any("SubjectGroup" in i for i in result["sanity_issues"])


def test_diagnose_infeasibility_returns_all_keys():
    result = diagnose_infeasibility([], [], [], [], 5, 5)
    assert "sanity_issues" in result
    assert "suspects" in result
    assert "entity_conflicts" in result
    assert "cleared" in result
