"""Enforce SubjectGroup constraints.

Two modes:
- Fully-shared (shared_hours is None): all subjects in the group must be
  assigned to the same slots (current behavior).
- Partial-share (shared_hours is set): exactly shared_hours slots must have
  all members active; remaining hours can be standalone per subject.
"""

import json as _json

from .base import Restriction


def _is_line_included(entity, line_index):
    raw = getattr(entity, "included_lines", None)
    if raw is None:
        return True
    if isinstance(raw, str):
        try:
            included = _json.loads(raw)
        except (ValueError, TypeError):
            return True
    else:
        included = raw
    if not isinstance(included, list):
        return True
    return line_index in included


def _get_subject_ids(sg):
    if hasattr(sg, 'subjects') and sg.subjects:
        return [s.id for s in sg.subjects]
    if hasattr(sg, 'subject_ids') and sg.subject_ids:
        return sg.subject_ids
    return []


class SubjectGroupAssignment(Restriction):
    def apply(self, model, assignments, all_groups, all_subjects, all_subjectgroups):
        for sg in all_subjectgroups:
            subject_ids = _get_subject_ids(sg)
            if len(subject_ids) < 2:
                continue

            shared_hours = getattr(sg, 'shared_hours', None)
            if shared_hours is not None:
                self._apply_partial(model, assignments, all_groups, sg, subject_ids, shared_hours)
            else:
                self._apply_fully_shared(model, assignments, all_groups, sg, subject_ids)

    def _apply_fully_shared(self, model, assignments, all_groups, sg, subject_ids):
        for group in all_groups:
            _, line_letter = group.split("-")
            line_index = ord(line_letter) - ord("A")
            if not _is_line_included(sg, line_index):
                continue

            hours = set((k[3], k[4]) for k in assignments if k[0] == group)
            for (day, hour) in hours:
                for i in range(len(subject_ids)):
                    for j in range(i + 1, len(subject_ids)):
                        subj1_id = subject_ids[i]
                        subj2_id = subject_ids[j]

                        subj1_vars = [
                            assignments[k]
                            for k in assignments
                            if k[0] == group and k[1] == subj1_id and k[3] == day and k[4] == hour
                        ]
                        subj2_vars = [
                            assignments[k]
                            for k in assignments
                            if k[0] == group and k[1] == subj2_id and k[3] == day and k[4] == hour
                        ]

                        if subj1_vars and subj2_vars:
                            model.Add(sum(subj1_vars) == sum(subj2_vars))

    def _apply_partial(self, model, assignments, all_groups, sg, subject_ids, shared_hours):
        for group in all_groups:
            _, line_letter = group.split("-")
            line_index = ord(line_letter) - ord("A")
            if not _is_line_included(sg, line_index):
                continue

            all_slots = set((k[3], k[4]) for k in assignments if k[0] == group)
            shared_vars = []
            for (day, hour) in sorted(all_slots):
                active_vars = {}
                for subj_id in subject_ids:
                    subj_vars = [
                        assignments[k]
                        for k in assignments
                        if k[0] == group and k[1] == subj_id and k[3] == day and k[4] == hour
                    ]
                    if subj_vars:
                        active = model.NewBoolVar(
                            f"sg_{sg.id}_{subj_id}_act_{group}_d{day}_h{hour}"
                        )
                        model.Add(sum(subj_vars) == active)
                        active_vars[subj_id] = active

                if len(active_vars) >= len(subject_ids):
                    shared = model.NewBoolVar(
                        f"sg_{sg.id}_shared_{group}_d{day}_h{hour}"
                    )
                    active_list = list(active_vars.values())
                    for a in active_list:
                        model.Add(shared <= a)
                    model.Add(shared >= sum(active_list) - (len(active_list) - 1))
                    shared_vars.append(shared)

            if shared_vars:
                model.Add(sum(shared_vars) == shared_hours)
