from backend.populate_db import populate_db
from backend.models import Session, Course, Subject, Teacher, Config, Timeslot


def test_populate_db_creates_entries(tmp_path):
    # Run populate_db which recreates the sqlite file referenced by the project
    populate_db()
    session = Session()
    # Config should exist
    cfg = session.query(Config).first()
    assert cfg is not None
    # At least one course, subject and teacher should exist
    assert session.query(Course).count() >= 1
    assert session.query(Subject).count() >= 1
    assert session.query(Teacher).count() >= 1
    # Timeslots were created
    assert session.query(Timeslot).count() >= 1
    session.close()
