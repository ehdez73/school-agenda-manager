from backend.populate_db import populate_db
from backend.models import Session, TimeSlotAssignment, Timeslot, Subject, SubjectGroup, Teacher
from backend.timetable import get_timetables_from_db, print_markdown_timetable_from_assignments, print_markdown_timetable_per_teacher


def setup_db_and_assignment():
    populate_db()
    session = Session()
    # pick one existing timeslot and subject/teacher
    ts = session.query(Timeslot).first()
    subj = session.query(Subject).first()
    teacher = session.query(Teacher).first()
    # create assignment linking them
    assignment = TimeSlotAssignment(timeslot=ts, subject_id=subj.id, teacher_id=teacher.id, subject=subj, teacher=teacher)
    session.add(assignment)
    session.commit()
    return session


def test_get_timetables_and_prints():
    session = setup_db_and_assignment()
    tables = get_timetables_from_db(session)
    assert isinstance(tables, dict)
    md = print_markdown_timetable_from_assignments(session)
    assert isinstance(md, str)
    assert "##" in md
    md2 = print_markdown_timetable_per_teacher(session)
    assert isinstance(md2, str)
    assert "##" in md2
    session.close()


def test_get_timetables_uses_subject_group_color_for_grouped_slots():
    populate_db()
    session = Session()

    rel = session.query(Subject).filter_by(id="REL1").one()
    val = session.query(Subject).filter_by(id="VAL1").one()
    rel.color = "#111111"
    val.color = "#222222"

    rel_teacher = session.query(Teacher).filter(Teacher.subjects.any(id="REL1")).first()
    val_teacher = session.query(Teacher).filter(Teacher.subjects.any(id="VAL1")).first()
    subject_group = session.query(SubjectGroup).filter(SubjectGroup.subjects.any(id="REL1")).first()
    subject_group.color = "#ffaa00"

    ts = Timeslot(day=0, hour=0, course_id="1º", line=0, subject_group=subject_group)
    session.add(ts)
    session.flush()
    session.add(TimeSlotAssignment(timeslot=ts, subject=rel, teacher=rel_teacher, subject_id=rel.id, teacher_id=rel_teacher.id))
    session.add(TimeSlotAssignment(timeslot=ts, subject=val, teacher=val_teacher, subject_id=val.id, teacher_id=val_teacher.id))
    session.commit()

    tables = get_timetables_from_db(session)
    cell = tables["1ºA"][(0, 0)]
    assert len(cell) == 2
    assert all('background-color: #ffaa00' in entry for entry in cell)
    assert all('#111111' not in entry and '#222222' not in entry for entry in cell)

    session.close()
