"""Enforce max hours per day for a subject in a group when taught by a teacher."""

from .base import Restriction


class GroupSubjectMaxHoursPerDay(Restriction):
    """Enforce that for each group, subject, teacher and day, the number of hours assigned
    does not exceed subject.max_hours_per_day.
    """

    def apply(self, model, assignments, groups, subjects, teachers, num_days):
        for group in groups:
            course = group.split('-')[0]
            for subject in subjects:
                if subject.course_id == course:
                    for teacher in teachers:
                        if subject in teacher.subjects:
                            for d in range(num_days):
                                hour_vars = [
                                    assignments[key]
                                    for key in assignments
                                    if key[0] == group and key[1] == subject.id and key[2] == teacher.id and key[3] == d
                                ]
                                model.Add(sum(hour_vars) <= subject.max_hours_per_day)
