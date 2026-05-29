"""Ensure at most one teacher is assigned per group-subject combination."""

from .base import Restriction


class TeacherOneSubjectPerGroup(Restriction):
    """
    Restriction to ensure that for each group+subject combination,
    at most one teacher is assigned across all slots.

    This prevents multiple teachers from sharing the same subject in the same group.
    """

    def apply(self, model, assignments, teachers, groups, subjects):
        self._apply_impl(model, assignments, teachers, groups, subjects)

    def apply_with_assumptions(self, model, assignments, teachers, groups, subjects):
        return self._apply_impl(model, assignments, teachers, groups, subjects,
                                diagnostic_mode=True)

    def _apply_impl(self, model, assignments, teachers, groups, subjects,
                    diagnostic_mode=False):
        assumptions = []
        for group in groups:
            course = group.split("-")[0]
            for subject in subjects:
                if subject.course_id != course:
                    continue

                # Build per-teacher activity indicators
                teacher_active = []
                for teacher in teachers:
                    teacher_vars = [
                        assignments[key]
                        for key in assignments
                        if key[0] == group
                        and key[1] == subject.id
                        and key[2] == teacher.id
                    ]
                    if not teacher_vars:
                        continue

                    # teacher_active[t] == 1 iff this teacher has any hour assigned
                    t_active = model.NewBoolVar(
                        f"one_teacher_{group}_{subject.id}_{teacher.id}"
                    )
                    total = sum(teacher_vars)
                    model.Add(total >= 1).OnlyEnforceIf(t_active)
                    model.Add(total == 0).OnlyEnforceIf(t_active.Not())
                    teacher_active.append(t_active)

                # At most one teacher active for this (group, subject)
                if len(teacher_active) > 1:
                    if diagnostic_mode:
                        assume = model.NewBoolVar(
                            f"assume_one_teacher_{group}_{subject.id}"
                        )
                        model.Add(sum(teacher_active) <= 1).OnlyEnforceIf(assume)
                        assumptions.append((assume, {
                            "restriction": "TeacherOneSubjectPerGroup",
                            "entity_type": "subject",
                            "entity_id": subject.id,
                            "entity_name": subject.name,
                            "extra": {"group": group},
                        }))
                    else:
                        model.Add(sum(teacher_active) <= 1)
        return assumptions
