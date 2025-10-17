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

                    # For any pair of hours that are NOT consecutive, forbid both subjects
                    # occupying those two hours on the same day for the same group.
                    for ha in range(num_hours):
                        for hb in range(num_hours):
                            if abs(ha - hb) > 1:
                                model.Add(y_s[ha] + y_t[hb] <= 1)
