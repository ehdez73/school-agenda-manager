"""Require that multiple hours of the same subject for a group on a day are consecutive."""

from .base import Restriction


class GroupSubjectHoursMustBeConsecutive(Restriction):
    """If a subject is taught more than one hour per day in a group, those hours must
    form a single contiguous block (consecutive hours).
    """

    def apply(self, model, assignments, groups, subjects, num_days, num_hours):
        for group in groups:
            course = group.split('-')[0]
            for subject in subjects:
                if subject.course_id == course:
                    for d in range(num_days):
                        # 1) create aggregated variables y_h
                        y_vars = []
                        for h in range(num_hours):
                            y = model.NewBoolVar(f"y_{group}_{subject.id}_d{d}_h{h}")
                            assign_vars = [
                                assignments[key]
                                for key in assignments
                                if key[0] == group and key[1] == subject.id and key[3] == d and key[4] == h
                            ]
                            if assign_vars:
                                model.Add(sum(assign_vars) == y)
                            else:
                                model.Add(y == 0)
                            y_vars.append(y)

                        # 2) define starts: start_h = 1 if y_h == 1 and y_{h-1} == 0
                        starts = []
                        for h in range(num_hours):
                            s = model.NewBoolVar(f"start_{group}_{subject.id}_d{d}_h{h}")
                            starts.append(s)
                            if h == 0:
                                model.Add(s == y_vars[0])
                            else:
                                model.Add(s >= y_vars[h] - y_vars[h-1])
                                model.Add(s <= y_vars[h])
                                model.Add(s <= 1 - y_vars[h-1])

                        # 3) at most one block start per day -> ensures a single contiguous block (or none)
                        model.Add(sum(starts) <= 1)
