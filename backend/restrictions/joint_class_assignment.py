"""Enforce JointClass constraints: multiple lines share the same subject, teacher, and slot.

Two modes:
- Fixed teacher (teacher_id is set): all lines use that teacher.
- Solver-chooses teacher (teacher_id is None): any qualified teacher, but
  must be the same teacher for all lines at any given slot.

Two share modes (via shared_hours):
- Fully-shared (shared_hours is None): all weekly hours are taught jointly.
- Partial-share (shared_hours is set): exactly N hours are joint; remaining
  hours are standalone per line.
"""

import json

from .base import Restriction


def build_joint_class_lookup(joint_classes, all_teachers=None,
                              num_days=5, num_hours=5):
    """Build a lookup dict for joint class data.

    Args:
        joint_classes: List of JointClass objects.
        all_teachers: List of Teacher objects (needed when teacher_id is None).
        num_days: Number of days per week.
        num_hours: Number of hours per day.

    Returns:
        dict: {(teacher_id, subject_id, day, hour) -> {
            "jc_id": int,
            "num_lines": int,
            "first_group": str,
            "groups": list[str],
            "course_id": str,
            "subject_id": str,
        }}
    """
    lookup = {}
    for jc in joint_classes or []:
        lines = json.loads(jc.lines) if isinstance(jc.lines, str) else (jc.lines or [])
        if not lines:
            continue
        groups = [f"{jc.course_id}-{line}" for line in lines]
        first_group = groups[0]
        num_lines = len(lines)

        teachers = []
        if jc.teacher_id is not None:
            teachers = [jc.teacher_id]
        elif all_teachers:
            for t in all_teachers:
                if any(s.id == jc.subject_id for s in getattr(t, 'subjects', [])):
                    teachers.append(t.id)

        for tid in teachers:
            for d in range(num_days):
                for h in range(num_hours):
                    key = (tid, jc.subject_id, d, h)
                    lookup[key] = {
                        "jc_id": jc.id,
                        "num_lines": num_lines,
                        "first_group": first_group,
                        "groups": groups,
                        "course_id": jc.course_id,
                        "subject_id": jc.subject_id,
                    }
    return lookup


class JointClassAssignment(Restriction):
    """Force multiple lines to share the same subject, teacher, and slot."""

    def apply(self, model, assignments, all_groups, num_days, num_hours,
              joint_classes, all_teachers=None):
        if not joint_classes:
            return

        for jc in joint_classes:
            lines = json.loads(jc.lines) if isinstance(jc.lines, str) else (jc.lines or [])
            if len(lines) < 2:
                continue

            course = jc.course_id
            subject_id = jc.subject_id
            shared_hours = getattr(jc, 'shared_hours', None)

            if jc.teacher_id is not None:
                self._apply_fixed_teacher(
                    model, assignments, course, subject_id, jc.teacher_id,
                    lines, num_days, num_hours, shared_hours,
                )
            else:
                self._apply_solver_chooses_teacher(
                    model, assignments, course, subject_id,
                    lines, num_days, num_hours, shared_hours, all_teachers,
                )

    def _apply_fixed_teacher(self, model, assignments, course, subject_id,
                              teacher_id, lines, num_days, num_hours,
                              shared_hours):
        if shared_hours is not None:
            self._apply_fixed_teacher_partial(
                model, assignments, course, subject_id, teacher_id,
                lines, num_days, num_hours, shared_hours,
            )
        else:
            self._apply_fixed_teacher_all_joint(
                model, assignments, course, subject_id, teacher_id,
                lines, num_days, num_hours,
            )

    def _apply_fixed_teacher_all_joint(self, model, assignments, course,
                                        subject_id, teacher_id, lines,
                                        num_days, num_hours):
        first_group = f"{course}-{lines[0]}"
        for d in range(num_days):
            for h in range(num_hours):
                ref_key = (first_group, subject_id, teacher_id, d, h)
                if ref_key not in assignments:
                    continue
                for line_letter in lines[1:]:
                    other_group = f"{course}-{line_letter}"
                    other_key = (other_group, subject_id, teacher_id, d, h)
                    if other_key in assignments:
                        model.Add(assignments[ref_key] == assignments[other_key])

    def _apply_fixed_teacher_partial(self, model, assignments, course,
                                      subject_id, teacher_id, lines,
                                      num_days, num_hours, shared_hours):
        groups = [f"{course}-{l}" for l in lines]
        num_lines = len(lines)
        shared_vars = []
        for d in range(num_days):
            for h in range(num_hours):
                line_vars = []
                for group in groups:
                    key = (group, subject_id, teacher_id, d, h)
                    if key in assignments:
                        line_vars.append(assignments[key])
                if len(line_vars) >= num_lines:
                    shared = model.NewBoolVar(
                        f"shared_{course}_{subject_id}_{teacher_id}_d{d}_h{h}"
                    )
                    for var in line_vars:
                        model.Add(shared <= var)
                    model.Add(shared >= sum(line_vars) - (num_lines - 1))
                    shared_vars.append(shared)
        if shared_vars:
            model.Add(sum(shared_vars) == shared_hours)

    def _apply_solver_chooses_teacher(self, model, assignments, course,
                                       subject_id, lines, num_days, num_hours,
                                       shared_hours, all_teachers):
        if not all_teachers:
            return

        qualified = [
            t for t in all_teachers
            if hasattr(t, 'subjects') and any(s.id == subject_id for s in t.subjects)
        ]
        if not qualified:
            return

        groups = [f"{course}-{l}" for l in lines]
        num_lines = len(lines)

        if shared_hours is not None:
            self._apply_solver_chooses_teacher_partial(
                model, assignments, groups, subject_id, qualified,
                num_days, num_hours, shared_hours, num_lines,
            )
        else:
            self._apply_solver_chooses_teacher_all_joint(
                model, assignments, groups, subject_id, qualified,
                num_days, num_hours,
            )

    def _apply_solver_chooses_teacher_all_joint(self, model, assignments,
                                                  groups, subject_id,
                                                  qualified, num_days,
                                                  num_hours):
        for d in range(num_days):
            for h in range(num_hours):
                for teacher in qualified:
                    first_key = (groups[0], subject_id, teacher.id, d, h)
                    if first_key not in assignments:
                        continue
                    for other_group in groups[1:]:
                        other_key = (other_group, subject_id, teacher.id, d, h)
                        if other_key in assignments:
                            model.Add(assignments[first_key] == assignments[other_key])

                teacher_active = []
                for t in qualified:
                    first_key = (groups[0], subject_id, t.id, d, h)
                    if first_key in assignments:
                        teacher_active.append(assignments[first_key])
                if len(teacher_active) > 1:
                    model.AddAtMostOne(teacher_active)

    def _apply_solver_chooses_teacher_partial(self, model, assignments,
                                               groups, subject_id,
                                               qualified, num_days,
                                               num_hours, shared_hours,
                                               num_lines):
        for d in range(num_days):
            for h in range(num_hours):
                for teacher in qualified:
                    first_key = (groups[0], subject_id, teacher.id, d, h)
                    if first_key not in assignments:
                        continue
                    for other_group in groups[1:]:
                        other_key = (other_group, subject_id, teacher.id, d, h)
                        if other_key in assignments:
                            model.Add(assignments[first_key] == assignments[other_key])

                teacher_active = []
                for t in qualified:
                    first_key = (groups[0], subject_id, t.id, d, h)
                    if first_key in assignments:
                        teacher_active.append(assignments[first_key])
                if len(teacher_active) > 1:
                    model.AddAtMostOne(teacher_active)

        shared_vars = []
        for d in range(num_days):
            for h in range(num_hours):
                all_line_vars = {g: [] for g in groups}
                for teacher in qualified:
                    for group in groups:
                        key = (group, subject_id, teacher.id, d, h)
                        if key in assignments:
                            all_line_vars[group].append(assignments[key])

                if any(len(v) == 0 for v in all_line_vars.values()):
                    continue

                group_active = {}
                for group in groups:
                    if len(all_line_vars[group]) == 1:
                        group_active[group] = all_line_vars[group][0]
                    else:
                        ga = model.NewBoolVar(
                            f"ga_{group}_{subject_id}_d{d}_h{h}"
                        )
                        model.Add(ga <= sum(all_line_vars[group]))
                        model.Add(sum(all_line_vars[group]) <= len(all_line_vars[group]) * ga)
                        group_active[group] = ga

                shared = model.NewBoolVar(
                    f"shared_sc_{subject_id}_d{d}_h{h}"
                )
                active_list = list(group_active.values())
                for a in active_list:
                    model.Add(shared <= a)
                model.Add(shared >= sum(active_list) - (num_lines - 1))
                shared_vars.append(shared)

        if shared_vars:
            model.Add(sum(shared_vars) == shared_hours)
