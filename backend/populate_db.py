from .models import ENGINE, Session, Course, Subject, Teacher, Timeslot, Config
from sqlalchemy import inspect
from .models import Base
from .models import SubjectGroup
import json
from . import export_import as shared_export_import
import os


def populate_db(init_file: str | None = None):
    """Create (recreate) the database schema.

    If init_file is provided and exists, import data from that JSON file
    immediately after creating the schema.
    """
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
    print("Database created.")

    # If an init JSON file is provided, import it using the shared import logic
    if init_file:
        try:
            if os.path.exists(init_file):
                print(f"Importing initial data from {init_file}...")
                with open(init_file, "r", encoding="utf-8") as fh:
                    payload = json.load(fh)
                session = Session()
                try:
                    shared_export_import.import_payload(session, payload)
                    session.commit()
                    print("Initial data imported.")
                except Exception as e:
                    session.rollback()
                    print(f"Failed to import initial data: {e}")
                finally:
                    session.close()
            else:
                print(f"Init file {init_file} does not exist; skipping import.")
        except Exception as e:
            print(f"Error while importing init file: {e}")


def init_config(session):
    DEFAULT_HOUR_NAMES = ["9:00", "10:00", "11:00", "12:00", "13:00"]
    DEFAULT_DAY_INDICES = [0, 1, 2, 3, 4]  # Monday to Friday
    session.add(
        Config(
            classes_per_day=5,
            days_per_week=5,
            hour_names=json.dumps(DEFAULT_HOUR_NAMES),
            day_indices=json.dumps(DEFAULT_DAY_INDICES),
        )
    )


def init_dummy_data(session):
    course_1 = Course(id="1º", num_lines=2)
    course_2 = Course(id="2º", num_lines=2)
    course_3 = Course(id="3º", num_lines=2)

    courses = [
        course_1,
        course_2,
        course_3,
    ]
    session.add_all(courses)

    math1 = Subject(
        id="MAT1",
        name="Matemáticas",
        weekly_hours=6,
        max_hours_per_day=2,
        course=course_1,
        teach_every_day=True,
    )
    lang1 = Subject(
        id="LEN1",
        name="Lengua",
        weekly_hours=6,
        max_hours_per_day=2,
        course=course_1,
        teach_every_day=True,
    )
    val1 = Subject(
        id="VAL1",
        name="Valores",
        weekly_hours=1,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    rel1 = Subject(
        id="REL1",
        name="Religión",
        weekly_hours=1,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    sci1 = Subject(
        id="CIE1",
        name="Ciencias",
        weekly_hours=2,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    eng1 = Subject(
        id="ING1",
        name="Inglés",
        weekly_hours=4,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    mus1 = Subject(
        id="MUS1",
        name="Música",
        weekly_hours=1,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    art1 = Subject(
        id="ART1",
        name="Educación Plástica",
        weekly_hours=1,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    soc1 = Subject(
        id="SOC1",
        name="Sociales",
        weekly_hours=2,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    ef1 = Subject(
        id="EFI1",
        name="Educación Física",
        weekly_hours=2,
        max_hours_per_day=1,
        course=course_1,
        teach_every_day=False,
    )
    subjects1 = [
        math1,
        lang1,
        val1,
        rel1,
        sci1,
        eng1,
        mus1,
        art1,
        soc1,
        ef1,
    ]

    subjects = []
    subjects.extend(subjects1)

    session.add_all(subjects)
    for subject in subjects1:
        print(
            f"Subject: {subject.name} -(ID: {subject.id}) - {subject.weekly_hours} weekly hours - max:{subject.max_hours_per_day} hours/day"
        )

    val_rel_group = SubjectGroup(id="1", name="VAL-REL-1", subjects=[val1, rel1])
    session.add(val_rel_group)
    print(
        f"SubjectGroup: {val_rel_group.name} - Subjects: {[s.name for s in val_rel_group.subjects]}"
    )
    teachers = [
        Teacher(name="Ana", max_hours_week=20, subjects=[math1], tutor_group="1ºA"),
        Teacher(name="Luis", max_hours_week=20, subjects=[lang1]),
        Teacher(name="María", max_hours_week=20, subjects=[val1, mus1, ef1]),
        Teacher(name="Fernando", max_hours_week=10, subjects=[rel1, art1, soc1]),
        Teacher(name="Carmen", max_hours_week=20, subjects=[sci1, eng1]),
    ]
    session.add_all(teachers)

    for teacher in teachers:
        print(f"Teacher: {teacher.name} - {teacher.max_hours_week} weekly hours")
        for subject in teacher.subjects:
            print(f"  - {subject.name} (ID: {subject.id})")

    timeslots = []
    # Store weekday as an integer index (0 = first weekday).
    days = [0, 1, 2, 3, 4]  # Lunes..Viernes
    for course in courses:
        for line in range(1, 3):
            for day in days:
                for hour in range(8, 13):
                    timeslots.append(
                        Timeslot(day=day, hour=hour, course_id=course.id, line=line)
                    )
    session.add_all(timeslots)
    print(f"Created {len(timeslots)} timeslots.")
    session.commit()
    session.close()
    print("Database populated with example data using SQLAlchemy.")


if __name__ == "__main__":
    # If a JSON export file is provided as the first argument, import it
    import sys

    # If a JSON export file is provided as the first argument, pass it to populate_db
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        populate_db(sys.argv[1])
    elif len(sys.argv) > 1:
        print(f"Provided init file {sys.argv[1]} not found; creating empty DB.")
        populate_db()
    else:
        populate_db()
