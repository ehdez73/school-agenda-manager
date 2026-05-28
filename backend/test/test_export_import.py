"""Tests that export/import (backup/restore) preserves all Subject fields."""
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Base, Subject, Course
from backend.export_import import dump_db, import_payload


@pytest.fixture()
def memory_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def _seed(session):
    """Insert a course and two subjects with non-default field values."""
    course = Course(id="1º", num_lines=2)
    session.add(course)
    session.flush()

    s1 = Subject(
        id="MAT1",
        name="Maths",
        color="#123456",
        weekly_hours=5,
        max_hours_per_day=2,
        consecutive_hours=False,   # non-default
        teach_every_day=True,      # non-default
        course_id="1º",
        linked_subject_id=None,
        included_lines=json.dumps([0, 1]),
    )
    s2 = Subject(
        id="LEN1",
        name="Language",
        color="#abcdef",
        weekly_hours=3,
        max_hours_per_day=1,
        consecutive_hours=True,
        teach_every_day=False,
        course_id="1º",
        linked_subject_id=None,
        included_lines=None,
    )
    session.add_all([s1, s2])
    session.flush()


def test_subject_fields_round_trip(memory_session):
    """All Subject columns survive a dump → import cycle."""
    _seed(memory_session)

    # Export
    payload = dump_db(memory_session)
    assert len(payload["subjects"]) == 2

    # Verify that dump includes the fields
    mat = next(s for s in payload["subjects"] if s["id"] == "MAT1")
    assert mat["color"] == "#123456"
    assert mat["consecutive_hours"] is False
    assert mat["teach_every_day"] is True
    assert mat["max_hours_per_day"] == 2
    assert mat["weekly_hours"] == 5
    assert mat["included_lines"] == [0, 1]

    # Wipe and re-import into the same (now empty) session
    memory_session.query(Subject).delete()
    memory_session.query(Course).delete()
    memory_session.flush()

    import_payload(memory_session, payload)

    # Verify restored values
    restored = memory_session.get(Subject, "MAT1")
    assert restored is not None
    assert restored.consecutive_hours is False,  "consecutive_hours not restored"
    assert restored.teach_every_day is True,     "teach_every_day not restored"
    assert restored.max_hours_per_day == 2,      "max_hours_per_day not restored"
    assert restored.weekly_hours == 5,           "weekly_hours not restored"
    assert restored.color == "#123456",         "color not restored"
    assert json.loads(restored.included_lines) == [0, 1], "included_lines not restored"

    restored2 = memory_session.get(Subject, "LEN1")
    assert restored2.consecutive_hours is True
    assert restored2.teach_every_day is False
    assert restored2.color == "#abcdef"
    assert restored2.included_lines is None
