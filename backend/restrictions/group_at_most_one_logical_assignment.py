"""Ensure at most one logical assignment per group/day/hour, respecting SubjectGroups.

With partial-share SubjectGroups (shared_hours is set), a subject may be either
part of a fully-present SubjectGroup (one logical unit) or standalone, depending
on which other group members are active at that slot.
"""

from .base import Restriction


def _get_subject_ids(sg):
    if hasattr(sg, 'subjects') and sg.subjects:
        return [s.id for s in sg.subjects]
    if hasattr(sg, 'subject_ids') and sg.subject_ids:
        return sg.subject_ids
    return []


class GroupAtMostOneLogicalAssignment(Restriction):
    def apply(self, model, assignments, all_groups, num_days, num_hours, all_subjectgroups=None):
        fully_shared_subjects = set()
        fully_shared_map = {}
        partial_sgs = []

        if all_subjectgroups:
            for sg in all_subjectgroups:
                subject_ids = _get_subject_ids(sg)
                if len(subject_ids) < 2:
                    continue
                if getattr(sg, 'shared_hours', None) is not None:
                    partial_sgs.append((sg.id, subject_ids))
                else:
                    for subj_id in subject_ids:
                        fully_shared_subjects.add(subj_id)
                        fully_shared_map[subj_id] = sg.id

        for group in all_groups:
            for d in range(num_days):
                for h in range(num_hours):
                    slot_assignments = [
                        k for k in assignments
                        if k[0] == group and k[3] == d and k[4] == h
                    ]

                    if not slot_assignments:
                        continue

                    # --- Fully-shared SGs and standalone subjects ---
                    logical_units = {}
                    for k in slot_assignments:
                        subject_id = k[1]

                        if subject_id in fully_shared_subjects:
                            unit_id = f"subjectgroup_{fully_shared_map[subject_id]}"
                        elif not any(subject_id in sg_subjects for _, sg_subjects in partial_sgs):
                            unit_id = f"standalone_{subject_id}"
                        else:
                            continue

                        if unit_id not in logical_units:
                            logical_units[unit_id] = []
                        logical_units[unit_id].append(k)

                    logical_vars = []
                    for unit_id, unit_assignments in logical_units.items():
                        if unit_assignments:
                            unit_vars = [assignments[k] for k in unit_assignments]
                            if len(unit_vars) == 1:
                                logical_vars.append(unit_vars[0])
                            else:
                                unit_var = model.NewBoolVar(f"logical_unit_{group}_{d}_{h}_{unit_id}")
                                model.Add(unit_var <= sum(unit_vars))
                                model.Add(sum(unit_vars) <= len(unit_vars) * unit_var)
                                logical_vars.append(unit_var)

                    # --- Partial-share SGs: per-slot detection ---
                    for sg_id, subject_ids in partial_sgs:
                        member_active = {}
                        for subj_id in subject_ids:
                            subj_vars = [
                                assignments[k] for k in slot_assignments
                                if k[1] == subj_id
                            ]
                            if subj_vars:
                                active = model.NewBoolVar(
                                    f"partial_mem_{sg_id}_{subj_id}_{group}_{d}_{h}"
                                )
                                model.Add(sum(subj_vars) == active)
                                member_active[subj_id] = active

                        if not member_active:
                            continue

                        if len(member_active) >= len(subject_ids):
                            sg_present = model.NewBoolVar(
                                f"partial_sg_{sg_id}_full_{group}_{d}_{h}"
                            )
                            active_list = list(member_active.values())
                            for a in active_list:
                                model.Add(sg_present <= a)
                            model.Add(
                                sg_present >= sum(active_list) - (len(active_list) - 1)
                            )
                            logical_vars.append(sg_present)

                            for subj_id, active in member_active.items():
                                standalone = model.NewBoolVar(
                                    f"partial_std_{sg_id}_{subj_id}_{group}_{d}_{h}"
                                )
                                model.Add(standalone <= active)
                                model.Add(standalone <= 1 - sg_present)
                                model.Add(standalone >= active - sg_present)
                                logical_vars.append(standalone)
                        else:
                            for subj_id, active in member_active.items():
                                logical_vars.append(active)

                    if len(logical_vars) > 1:
                        model.Add(sum(logical_vars) <= 1)
