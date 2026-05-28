from backend.populate_db import populate_db
from backend.models import Session, Timeslot, TimeSlotAssignment, Subject, SubjectGroup, Teacher
from backend.scheduler import save_solution_to_db


class FakeSolver:
    def __init__(self, ones=None):
        # ones is a set of keys that should be considered active
        self.ones = set(ones or [])

    def Value(self, var):
        # In our test we will pass the key tuple as the var
        return 1 if var in self.ones else 0


def test_save_solution_creates_assignments():
    populate_db()
    session = Session()
    # Derive groups from courses table
    from backend.models import Course, Subject, Teacher, Config

    groups = []
    for course in session.query(Course).all():
        for i in range(course.num_lines):
            groups.append(f"{course.id}-{chr(ord('A') + i)}")

    subjects = session.query(Subject).all()
    teachers = session.query(Teacher).all()
    config = session.query(Config).first()
    num_days = config.days_per_week
    num_hours = config.classes_per_day

    # Create assignments where we mark a single timeslot active: first group, first subject, first teacher at day 0 hour 0
    assignments = {}
    key = (groups[0], subjects[0].id, teachers[0].id, 0, 0)
    # We'll use the key itself as the var passed to solver.Value
    assignments[key] = key

    fake_solver = FakeSolver(ones=[key])

    # Run save
    save_solution_to_db(session, fake_solver, assignments, groups, num_days, num_hours)

    # There should be at least one TimeSlotAssignment saved
    count = session.query(TimeSlotAssignment).count()
    assert count >= 1
    session.close()


def test_save_solution_sets_subject_group_id_for_grouped_slot():
    populate_db()
    session = Session()

    from backend.models import Course

    groups = []
    for course in session.query(Course).all():
        for i in range(course.num_lines):
            groups.append(f"{course.id}-{chr(ord('A') + i)}")

    first_group = groups[0]

    rel = session.query(Subject).filter_by(id="REL1").one()
    val = session.query(Subject).filter_by(id="VAL1").one()
    rel_teacher = session.query(Teacher).filter(Teacher.subjects.any(id="REL1")).first()
    val_teacher = session.query(Teacher).filter(Teacher.subjects.any(id="VAL1")).first()
    subject_group = session.query(SubjectGroup).filter(SubjectGroup.subjects.any(id="REL1")).first()

    assignments = {}
    rel_key = (first_group, rel.id, rel_teacher.id, 0, 0)
    val_key = (first_group, val.id, val_teacher.id, 0, 0)
    assignments[rel_key] = rel_key
    assignments[val_key] = val_key

    fake_solver = FakeSolver(ones=[rel_key, val_key])
    save_solution_to_db(session, fake_solver, assignments, groups, num_days=5, num_hours=5)

    course_id, line_str = first_group.split("-")
    line_num = ord(line_str) - ord("A")
    slot = session.query(Timeslot).filter_by(day=0, hour=0, course_id=course_id, line=line_num).one()
    assert slot.subject_group_id == subject_group.id
    session.close()
