"""Enforce that linked subjects (when present) scheduled on the same day for a group
must be in consecutive hours (in any order).

This restriction assumes a single-directional link stored on Subject.linked_subject_id.
We treat a link as bidirectional for enforcement: if subject A links to B (A.linked_subject_id==B.id)
the constraint is also applied when evaluating B.
"""

from .base import Restriction


class LinkedSubjectsConsecutive(Restriction):
    """Enforce that linked subjects scheduled on the same day must occupy adjacent hours.

    Uses auxiliary BoolVars to model per-hour presence of each subject, then
    constrains adjacency and alternation between the pair when both appear
    on the same day.
    """

    def apply(self, model, assignments, groups, subjects, num_days, num_hours):
        # Build a mapping id->subject for quick lookup
        subj_map = {s.id: s for s in subjects}

        for group in groups:
            course = group.split("-")[0]
            for s in subjects:
                # only consider subjects that belong to this course
                if s.course_id != course:
                    continue

                linked_id = getattr(s, "linked_subject_id", None)
                if not linked_id:
                    continue

                # linked subject must exist in provided subjects and belong to same course
                t = subj_map.get(linked_id)
                if not t or t.course_id != course:
                    continue

                # For each day create aggregated y variables per hour for both subjects
                for d in range(num_days):
                    y_s = []
                    y_t = []
                    z_day = []
                    for h in range(num_hours):
                        ys = model.NewBoolVar(f"link_y_{group}_{s.id}_d{d}_h{h}")
                        yt = model.NewBoolVar(f"link_y_{group}_{t.id}_d{d}_h{h}")
                        z = model.NewBoolVar(f"link_z_{group}_{s.id}_{t.id}_d{d}_h{h}")

                        assign_vars_s = [
                            assignments[k]
                            for k in assignments
                            if k[0] == group
                            and k[1] == s.id
                            and k[3] == d
                            and k[4] == h
                        ]
                        assign_vars_t = [
                            assignments[k]
                            for k in assignments
                            if k[0] == group
                            and k[1] == t.id
                            and k[3] == d
                            and k[4] == h
                        ]

                        if assign_vars_s:
                            model.Add(sum(assign_vars_s) == ys)
                        else:
                            model.Add(ys == 0)

                        if assign_vars_t:
                            model.Add(sum(assign_vars_t) == yt)
                        else:
                            model.Add(yt == 0)

                        # z marks that either linked subject is scheduled at this hour.
                        model.Add(z >= ys)
                        model.Add(z >= yt)
                        model.Add(z <= ys + yt)

                        y_s.append(ys)
                        y_t.append(yt)
                        z_day.append(z)

                    # Activate the linked-subject constraints only when BOTH
                    # linked subjects appear at least once on this day.
                    present_s = model.NewBoolVar(f"link_present_{group}_{s.id}_d{d}")
                    present_t = model.NewBoolVar(f"link_present_{group}_{t.id}_d{d}")
                    both_present = model.NewBoolVar(
                        f"link_both_present_{group}_{s.id}_{t.id}_d{d}"
                    )

                    sum_s = sum(y_s)
                    sum_t = sum(y_t)

                    model.Add(sum_s >= 1).OnlyEnforceIf(present_s)
                    model.Add(sum_s == 0).OnlyEnforceIf(present_s.Not())

                    model.Add(sum_t >= 1).OnlyEnforceIf(present_t)
                    model.Add(sum_t == 0).OnlyEnforceIf(present_t.Not())

                    model.AddBoolAnd([present_s, present_t]).OnlyEnforceIf(both_present)
                    model.AddBoolOr([present_s.Not(), present_t.Not()]).OnlyEnforceIf(
                        both_present.Not()
                    )

                    # If both subjects are taught on the same day, they must be
                    # consecutive and alternate with each other.
                    for h in range(num_hours):
                        # Build list of adjacent hour indicators for t around h
                        adjacent_t = []
                        if h - 1 >= 0:
                            adjacent_t.append(y_t[h - 1])
                        if h + 1 < num_hours:
                            adjacent_t.append(y_t[h + 1])

                        if adjacent_t:
                            # If s is scheduled at h then at least one adjacent
                            # hour must host t.
                            model.Add(sum(adjacent_t) >= y_s[h]).OnlyEnforceIf(
                                both_present
                            )

                        # Symmetric constraint: if t at h then s must be adjacent
                        adjacent_s = []
                        if h - 1 >= 0:
                            adjacent_s.append(y_s[h - 1])
                        if h + 1 < num_hours:
                            adjacent_s.append(y_s[h + 1])

                        if adjacent_s:
                            model.Add(sum(adjacent_s) >= y_t[h]).OnlyEnforceIf(
                                both_present
                            )

                    # Avoid same-subject adjacency when both are present
                    # (forces alternation: M-L-M, L-M-L, etc.).
                    for h in range(num_hours - 1):
                        model.Add(y_s[h] + y_s[h + 1] <= 1).OnlyEnforceIf(
                            both_present
                        )
                        model.Add(y_t[h] + y_t[h + 1] <= 1).OnlyEnforceIf(
                            both_present
                        )

                    # Ensure all occurrences of either linked subject on the day
                    # are in a single contiguous block when both are present.
                    starts = []
                    for h in range(num_hours):
                        start = model.NewBoolVar(
                            f"link_start_{group}_{s.id}_{t.id}_d{d}_h{h}"
                        )
                        starts.append(start)
                        if h == 0:
                            model.Add(start == z_day[0])
                        else:
                            model.Add(start >= z_day[h] - z_day[h - 1])
                            model.Add(start <= z_day[h])
                            model.Add(start <= 1 - z_day[h - 1])

                    model.Add(sum(starts) <= 1).OnlyEnforceIf(both_present)
