"""Hard restriction: tutors must teach the first and last hour of the week

If a teacher is marked as tutor for a group (teacher.tutor_group), they must be
assigned to teach that group's first hour of the week (day=0,hour=0) and the
last hour of the week (day=num_days-1,hour=num_hours-1). This is enforced as
hard equality constraints on the corresponding assignment variables.
"""

from .base import Restriction


def normalize_group_name(group: str) -> str:
    """Normalizes group names to match scheduler format (adds dash before last char).

    Mirrors the helper in tutor_preference.py so inputs like "1ºA" become "1º-A".
    """
    if not group:
        return group
    if "-" in group:
        return group
    if len(group) > 1:
        return f"{group[:-1]}-{group[-1]}"
    return group


class TutorMandatoryHours(Restriction):
    """Require tutors to teach their group's first and last hours of the week.

    apply(model, assignments, teachers, num_days, num_hours, all_subjectgroups=None)
    """

    def apply(
        self, model, assignments, teachers, num_days, num_hours, all_subjectgroups=None
    ):
        # Determine first and last timeslots
        if num_days <= 0 or num_hours <= 0:
            return

        first_day, first_hour = 0, 0
        last_day, last_hour = num_days - 1, num_hours - 1

        for teacher in teachers:
            tutor_group = getattr(teacher, "tutor_group", None)
            if not tutor_group:
                continue

            normalized = normalize_group_name(tutor_group)
            # Build set of subject ids that belong to any SubjectGroup so we can
            # exclude them (subjectgroups imply desdoble / multiple subjects).
            subject_ids_in_groups = set()
            if all_subjectgroups:
                for sg in all_subjectgroups:
                    if hasattr(sg, "subjects") and sg.subjects:
                        subject_ids_in_groups.update({s.id for s in sg.subjects})
                    elif hasattr(sg, "subject_ids") and sg.subject_ids:
                        subject_ids_in_groups.update(set(sg.subject_ids))

            # Collect vars for the specific group taught by this teacher at the
            # first and last timeslots, excluding subjects that belong to a
            # SubjectGroup (we require a single subject in the timeslot).
            first_vars = [
                assignments[k]
                for k in assignments
                if k[0] == normalized
                and k[2] == teacher.id
                and k[3] == first_day
                and k[4] == first_hour
                and k[1] not in subject_ids_in_groups
            ]
            last_vars = [
                assignments[k]
                for k in assignments
                if k[0] == normalized
                and k[2] == teacher.id
                and k[3] == last_day
                and k[4] == last_hour
                and k[1] not in subject_ids_in_groups
            ]

            # If there are no variables for these slots, skip (possible if the
            # subject/teacher combination doesn't exist in assignments for that group)
            if first_vars:
                # At least one of the assignment variables for this teacher/group
                # at the first timeslot must be selected. If multiple subject
                # choices exist, exactly one should be selected; we enforce
                # sum(first_vars) == 1.
                model.Add(sum(first_vars) == 1)

            if last_vars:
                model.Add(sum(last_vars) == 1)
