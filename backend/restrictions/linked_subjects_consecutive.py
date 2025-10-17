"""Enforce that linked subjects (when present) scheduled on the same day for a group
must be in consecutive hours (in any order).

This restriction assumes a single-directional link stored on Subject.linked_subject_id.
We treat a link as bidirectional for enforcement: if subject A links to B (A.linked_subject_id==B.id)
the constraint is also applied when evaluating B.
"""

from .base import Restriction


class LinkedSubjectsConsecutive(Restriction):
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
                    for h in range(num_hours):
                        ys = model.NewBoolVar(f"link_y_{group}_{s.id}_d{d}_h{h}")
                        yt = model.NewBoolVar(f"link_y_{group}_{t.id}_d{d}_h{h}")

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

                        y_s.append(ys)
                        y_t.append(yt)

                    # Enforce pairing: every occurrence of s at hour h must have t
                    # at h-1 or h+1 (if those hours exist). Likewise, every
                    # occurrence of t must have s in an adjacent hour. This
                    # guarantees they appear as consecutive pairs (in any order)
                    # across the day for the same group.
                    for h in range(num_hours):
                        # Build list of adjacent hour indicators for t around h
                        adjacent_t = []
                        if h - 1 >= 0:
                            adjacent_t.append(y_t[h - 1])
                        if h + 1 < num_hours:
                            adjacent_t.append(y_t[h + 1])

                        if adjacent_t:
                            # If s is scheduled at h then sum(adjacent_t) >= 1
                            # i.e., at least one adjacent hour must host t.
                            model.Add(sum(adjacent_t) >= y_s[h])
                        else:
                            # No adjacent hours (single-hour day): cannot schedule s
                            model.Add(y_s[h] == 0)

                        # Symmetric constraint: if t at h then s must be adjacent
                        adjacent_s = []
                        if h - 1 >= 0:
                            adjacent_s.append(y_s[h - 1])
                        if h + 1 < num_hours:
                            adjacent_s.append(y_s[h + 1])

                        if adjacent_s:
                            model.Add(sum(adjacent_s) >= y_t[h])
                        else:
                            model.Add(y_t[h] == 0)
