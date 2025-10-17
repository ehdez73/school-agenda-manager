"""Require that multiple hours of the same subject for a group on a day are NOT consecutive.

This is the inverse of GroupSubjectHoursMustBeConsecutive: if a subject is taught
more than one hour per day in a group, those hours must NOT be adjacent.
"""

from .base import Restriction


class GroupSubjectHoursMustNotBeConsecutive(Restriction):
    """If a subject is taught more than one hour per day in a group, those hours must
    not be adjacent (no two consecutive hours).
    """

    def apply(self, model, assignments, groups, subjects, num_days, num_hours):
        for group in groups:
            course = group.split("-")[0]
            for subject in subjects:
                if subject.course_id == course:
                    for d in range(num_days):
                        # For each pair of adjacent hours, ensure they are not both assigned
                        for h in range(num_hours - 1):
                            # Build aggregated y_h for this subject/group/day/hour
                            assign_vars_h = [
                                assignments[key]
                                for key in assignments
                                if key[0] == group
                                and key[1] == subject.id
                                and key[3] == d
                                and key[4] == h
                            ]
                            assign_vars_h1 = [
                                assignments[key]
                                for key in assignments
                                if key[0] == group
                                and key[1] == subject.id
                                and key[3] == d
                                and key[4] == h + 1
                            ]

                            if assign_vars_h:
                                y_h = model.NewBoolVar(
                                    f"yn_{group}_{subject.id}_d{d}_h{h}"
                                )
                                model.Add(sum(assign_vars_h) == y_h)
                            else:
                                # no possible assignment at this hour -> treated as 0
                                y_h = None

                            if assign_vars_h1:
                                y_h1 = model.NewBoolVar(
                                    f"yn_{group}_{subject.id}_d{d}_h{h + 1}"
                                )
                                model.Add(sum(assign_vars_h1) == y_h1)
                            else:
                                y_h1 = None

                            if y_h is not None and y_h1 is not None:
                                # Prevent both being 1 at the same time
                                model.Add(y_h + y_h1 <= 1)
