from backend.populate_db import populate_db
from backend.models import Session, Timeslot, TimeSlotAssignment
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
