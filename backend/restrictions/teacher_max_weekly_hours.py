"""Ensure teachers do not exceed their weekly maximum teaching hours.

Joint classes (multiple groups sharing the same slot with the same teacher)
are counted once, not once per group.
"""

from .base import Restriction


class TeacherMaxWeeklyHours(Restriction):
    """Restrict each teacher to not exceed their maximum weekly hours.

    Joint classes are counted as a single hour (not per-group).
    """

    def apply(self, model, assignments, teachers, joint_lookup=None):
        self._apply_impl(model, assignments, teachers, joint_lookup=joint_lookup)

    def apply_with_assumptions(self, model, assignments, teachers, joint_lookup=None):
        return self._apply_impl(model, assignments, teachers,
                                diagnostic_mode=True, joint_lookup=joint_lookup)

    def _apply_impl(self, model, assignments, teachers, diagnostic_mode=False,
                    joint_lookup=None):
        if joint_lookup is None:
            joint_lookup = {}

        assumptions = []
        for teacher in teachers:
            coord = getattr(teacher, 'coordination_hours', 0) or 0
            effective_max = teacher.max_hours_week - coord

            seen_joint_slots = set()
            terms = []
            for key, var in assignments.items():
                if key[2] == teacher.id:
                    jc_key = (teacher.id, key[1], key[3], key[4])
                    jc_info = joint_lookup.get(jc_key)
                    jc_groups = jc_info.get("groups") if isinstance(jc_info, dict) else None
                    is_joint_member = jc_info and (
                        not jc_groups or key[0] in jc_groups
                    )

                    if is_joint_member:
                        slot_key = (
                            "jc",
                            jc_info.get("jc_id") if isinstance(jc_info, dict) else None,
                            key[3],
                            key[4],
                        )
                        if slot_key not in seen_joint_slots:
                            seen_joint_slots.add(slot_key)
                            terms.append(var)
                    else:
                        terms.append(var)

            total = sum(terms)
            if diagnostic_mode:
                assume = model.NewBoolVar(f"assume_maxh_{teacher.id}")
                model.Add(total <= effective_max).OnlyEnforceIf(assume)
                assumptions.append((assume, {
                    "restriction": "TeacherMaxWeeklyHours",
                    "entity_type": "teacher",
                    "entity_id": teacher.id,
                    "entity_name": teacher.name,
                    "extra": {"max_hours_week": teacher.max_hours_week,
                              "coordination_hours": coord,
                              "effective_max": effective_max},
                }))
            else:
                model.Add(total <= effective_max)
        return assumptions
