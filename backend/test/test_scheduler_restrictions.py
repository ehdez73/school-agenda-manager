from ortools.sat.python import cp_model

from backend.scheduler import _build_hard_restrictions


def test_hard_restrictions_include_group_subject_teacher_timeslot_limit():
    model = cp_model.CpModel()
    hard_restrictions = _build_hard_restrictions(
        model=model,
        assignments={},
        all_teachers=[],
        all_subjects=[],
        all_groups=[],
        all_subjectgroups=[],
        num_days=5,
        num_hours=6,
    )

    names = [name for name, _restriction, _args in hard_restrictions]
    assert "GroupSubjectAtMostOneTeacherPerTimeslot" in names
