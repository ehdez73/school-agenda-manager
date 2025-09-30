"""Module containing timetable scheduling restrictions as classes."""

from restrictions import Restriction


class SubjectWeeklyHours(Restriction):
    """Ensure each subject gets its required weekly hours for each group."""

    def apply(self, model, assignments, all_groups, all_subjects):
        for group in all_groups:
            course = group.split('-')[0]
            for subject in all_subjects:
                if subject.course_id == course:
                    # Sum all assignments for this group-subject combination
                    hours = sum(assignments[key] for key in assignments
                                if key[0] == group and key[1] == subject.id)
                    # Add constraint: must match required weekly hours
                    model.Add(hours == subject.weekly_hours)