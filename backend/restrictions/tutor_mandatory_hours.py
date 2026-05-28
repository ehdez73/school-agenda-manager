"""Soft constraint: reward tutors for teaching the first and last hour of the week

If a teacher is marked as tutor for a group (teacher.tutor_group), the solver
is rewarded when the tutor is assigned to that group's first hour (day=0,hour=0)
and the last hour (day=num_days-1,hour=num_hours-1). This is a soft constraint
added as preference terms in the objective, so it never causes infeasibility.
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
    """Reward tutors for teaching their group's first and last hours of the week.

    apply(model, assignments, teachers, num_days, num_hours, all_subjectgroups=None)
    """

    def __init__(self, weight: int = 500):
        self.weight = weight
        self.preference_terms = []

    def apply(
        self, model, assignments, teachers, num_days, num_hours, all_subjectgroups=None
    ):
        self.preference_terms = []
        self._apply_impl(model, assignments, teachers, num_days, num_hours,
                         all_subjectgroups)

    def apply_with_assumptions(
        self, model, assignments, teachers, num_days, num_hours, all_subjectgroups=None
    ):
        return self._apply_impl(model, assignments, teachers, num_days, num_hours,
                                all_subjectgroups, diagnostic_mode=True)

    def _apply_impl(
        self, model, assignments, teachers, num_days, num_hours,
        all_subjectgroups=None, diagnostic_mode=False,
    ):
        # Determine first and last timeslots
        if num_days <= 0 or num_hours <= 0:
            return []

        first_day, first_hour = 0, 0
        last_day, last_hour = num_days - 1, num_hours - 1

        # Build set of subject ids that belong to any SubjectGroup so we can
        # exclude them (subjectgroups imply desdoble / multiple subjects).
        subject_ids_in_groups = set()
        if all_subjectgroups:
            for sg in all_subjectgroups:
                if hasattr(sg, "subjects") and sg.subjects:
                    subject_ids_in_groups.update({s.id for s in sg.subjects})
                elif hasattr(sg, "subject_ids") and sg.subject_ids:
                    subject_ids_in_groups.update(set(sg.subject_ids))

        assumptions = []

        for teacher in teachers:
            tutor_group = getattr(teacher, "tutor_group", None)
            if not tutor_group:
                continue

            normalized = normalize_group_name(tutor_group)

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

            has_constraints = bool(first_vars) or bool(last_vars)

            if diagnostic_mode and has_constraints:
                assume = model.NewBoolVar(f"assume_tutor_{teacher.id}")
                if first_vars:
                    model.Add(sum(first_vars) == 1).OnlyEnforceIf(assume)
                if last_vars:
                    model.Add(sum(last_vars) == 1).OnlyEnforceIf(assume)
                assumptions.append((assume, {
                    "restriction": "TutorMandatoryHours",
                    "entity_type": "teacher",
                    "entity_id": teacher.id,
                    "entity_name": teacher.name,
                    "extra": {"tutor_group": normalized},
                }))
            elif not diagnostic_mode:
                # Soft constraint: reward the solver when the tutor is assigned
                # to the first and last timeslots. Since existing constraints
                # prevent >1 assignment per slot, sum(vars) is 0 or 1.
                if first_vars:
                    expr = sum(first_vars)
                    if self.weight != 1:
                        self.preference_terms.append(self.weight * expr)
                    else:
                        self.preference_terms.append(expr)
                if last_vars:
                    expr = sum(last_vars)
                    if self.weight != 1:
                        self.preference_terms.append(self.weight * expr)
                    else:
                        self.preference_terms.append(expr)

        return assumptions
