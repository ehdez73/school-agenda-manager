"""Enforce that certain subjects must be taught at least once each day.

This restriction checks Subject.teach_every_day and, for any subject where
that flag is True, forces the solver to schedule at least one assignment per
day for each group belonging to the subject's course.
"""

from .base import Restriction


class SubjectMustEveryDay(Restriction):
    def apply(self, model, assignments, all_groups, all_subjects, num_days):
        """Add constraints: for each group and subject with teach_every_day True,
        sum of assignments across teachers and hours for each day >= 1.

        assignments keys are expected to be tuples: (group, subject_id, teacher_id, day, hour)
        """
        # Build index of subjects that require daily presence
        daily_subject_ids = {
            s.id for s in all_subjects if getattr(s, "teach_every_day", False)
        }
        if not daily_subject_ids:
            return

        # Build a map of subject_id -> subject object to quickly check course membership
        subj_map = {s.id: s for s in all_subjects}
        for group in all_groups:
            course = group.split("-")[0]
            for subject_id in daily_subject_ids:
                subject_obj = subj_map.get(subject_id)
                if subject_obj is None:
                    continue
                # Only apply to subjects that belong to this course
                if getattr(subject_obj, "course_id", None) != course:
                    continue
                for d in range(num_days):
                    # collect all vars for this group, subject_id and day across teachers/hours
                    vars_for_day = [
                        var
                        for key, var in assignments.items()
                        if key[0] == group and key[1] == subject_id and key[3] == d
                    ]
                    if not vars_for_day:
                        # no variables for this combination, skip
                        continue
                    # enforce at least one scheduled slot per day
                    model.Add(sum(vars_for_day) >= 1)
