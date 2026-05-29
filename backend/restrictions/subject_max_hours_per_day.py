"""Restrict the maximum number of hours a subject can be scheduled per day across all groups."""

from .base import Restriction


class SubjectMaxHoursPerDay(Restriction):
    """
    Restriction to ensure that a subject is not scheduled for more than
    `max_hours_per_day` in a single day across any group.

    Note: This restriction groups by subject across ALL groups. For a per-group
    variant see GroupSubjectMaxHoursPerDay.
    """

    def apply(self, model, assignments, subjects, num_days):
        """
        Apply the restriction to the CP-SAT model.

        Args:
            model: CP-SAT CpModel instance.
            assignments: dict mapping (group, subject_id, teacher_id, day, hour) to BoolVars.
            subjects: list of Subject objects.
            num_days: number of days in the week.
        """
        for subject in subjects:
            max_hours = subject.max_hours_per_day
            for d in range(num_days):
                daily_vars = [
                    assignments[key]
                    for key in assignments
                    if key[1] == subject.id and key[3] == d
                ]
                if daily_vars:
                    model.Add(sum(daily_vars) <= max_hours)