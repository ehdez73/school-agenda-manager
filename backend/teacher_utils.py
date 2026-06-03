from sqlalchemy import func
from .models import Teacher, TimeSlotAssignment, SupportAssignment, Timeslot


def compute_teacher_hours(session):
    """
    Compute lective assigned hours, support hours, coordination hours,
    and max_hours_week for all teachers.

    Lective hours are counted as DISTINCT (day, hour) pairs from
    TimeSlotAssignment to avoid double-counting joint classes or
    split groups at the same time.

    Returns:
        dict[int, dict]: Mapping teacher_id -> {
            'name': str,
            'assigned_hours': int,
            'support_hours': int,
            'coordination_hours': int,
            'max_hours_week': int,
        }
    """
    teachers = session.query(Teacher).all()

    assigned_counts = {}
    for teacher_id, day, hour in session.query(
        TimeSlotAssignment.teacher_id, Timeslot.day, Timeslot.hour
    ).join(TimeSlotAssignment.timeslot).distinct().all():
        assigned_counts[teacher_id] = assigned_counts.get(teacher_id, 0) + 1

    support_counts = dict(
        session.query(
            SupportAssignment.teacher_id,
            func.count(SupportAssignment.id)
        ).group_by(SupportAssignment.teacher_id).all()
    )

    result = {}
    for t in teachers:
        result[t.id] = {
            'name': t.name,
            'assigned_hours': assigned_counts.get(t.id, 0),
            'support_hours': support_counts.get(t.id, 0),
            'coordination_hours': t.coordination_hours or 0,
            'max_hours_week': t.max_hours_week,
        }

    return result
