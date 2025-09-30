"""Ensure teachers do not exceed their weekly maximum teaching hours."""

from .base import Restriction


class TeacherMaxWeeklyHours(Restriction):
    """Restrict each teacher to not exceed their maximum weekly hours."""

    def apply(self, model, assignments, teachers):
        for teacher in teachers:
            max_hours = teacher.max_hours_week
            # Sum of all assignment vars for this teacher across days/hours
            total = sum(assignments[key] for key in assignments if key[2] == teacher.id)
            model.Add(total <= max_hours)
