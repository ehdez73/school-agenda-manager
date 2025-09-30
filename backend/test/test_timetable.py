from backend.populate_db import populate_db
from backend.models import Session, TimeSlotAssignment, Timeslot, Subject, Teacher
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
