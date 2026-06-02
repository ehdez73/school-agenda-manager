"""Teacher-related restriction: a teacher can teach at most one class per timeslot.

Joint classes (multiple groups sharing the same slot with the same teacher)
are counted as a single logical unit.
"""

from .base import Restriction


class TeacherOneClassAtATime(Restriction):
    """Restricts each teacher to teach at most one class in each time slot.

    Joint classes (multiple groups with the same teacher at the same slot)
    are treated as a single class.
    """

    def apply(self, model, assignments, teachers, num_days, num_hours,
              joint_lookup=None):
        if joint_lookup is None:
            joint_lookup = {}

        for teacher in teachers:
            for d in range(num_days):
                for h in range(num_hours):
                    slot_keys = [
                        k for k in assignments
                        if k[2] == teacher.id and k[3] == d and k[4] == h
                    ]
                    if not slot_keys:
                        continue

                    seen_joint = set()
                    logical_vars = []
                    for k in slot_keys:
                        jc_key = (teacher.id, k[1], d, h)
                        jc_info = joint_lookup.get(jc_key)
                        jc_groups = jc_info.get("groups") if isinstance(jc_info, dict) else None
                        is_joint_member = jc_info and (
                            not jc_groups or k[0] in jc_groups
                        )

                        if is_joint_member:
                            joint_token = (
                                "jc",
                                jc_info.get("jc_id") if isinstance(jc_info, dict) else None,
                                teacher.id,
                                k[1],
                                d,
                                h,
                            )
                            if joint_token not in seen_joint:
                                seen_joint.add(joint_token)
                                logical_vars.append(assignments[k])
                        else:
                            logical_vars.append(assignments[k])

                    if len(logical_vars) > 1:
                        model.AddAtMostOne(logical_vars)
