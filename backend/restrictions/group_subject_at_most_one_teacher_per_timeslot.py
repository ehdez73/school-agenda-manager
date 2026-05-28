"""Ensure one teacher per group-subject-timeslot."""

from collections import defaultdict

from .base import Restriction


class GroupSubjectAtMostOneTeacherPerTimeslot(Restriction):
    """For each (group, subject, day, hour), allow at most one teacher.

    This blocks duplicated assignments where the same subject appears twice in the
    same group and timeslot with different teachers.
    """

    def apply(self, model, assignments, all_groups, num_days, num_hours):
        del all_groups, num_days, num_hours  # Indexed directly from assignment keys.

        vars_by_group_subject_slot = defaultdict(list)
        for key, var in assignments.items():
            group, subject_id, _teacher_id, day, hour = key
            vars_by_group_subject_slot[(group, subject_id, day, hour)].append(var)

        for vars_in_slot in vars_by_group_subject_slot.values():
            if len(vars_in_slot) > 1:
                model.AddAtMostOne(vars_in_slot)