"""Ensure at most one teacher is assigned per group-subject combination."""

from .base import Restriction


class TeacherOneSubjectPerGroup(Restriction):
    """
    Restriction to ensure that for each group+subject combination,
    at most one teacher is assigned across all slots.

    This prevents multiple teachers from sharing the same subject in the same group.
    The original implementation had a bug: it used hardcoded range(5) for days/hours
    and summed total hours <= 1 instead of constraining teacher exclusivity.
    """

    def apply(self, model, assignments, teachers, groups, subjects):
        """
        Apply the restriction to the CP-SAT model.

        For each (group, subject) pair, creates a per-teacher BoolVar indicating
        whether that teacher has any assignment, then constrains at most one
        teacher to be active.

        Args:
            model: CP-SAT CpModel instance.
            assignments: dict mapping (group, subject_id, teacher_id, day, hour) to BoolVars.
            teachers: list of Teacher objects.
            groups: list of group identifiers.
            subjects: list of Subject objects.
        """
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
                    model.Add(sum(teacher_active) <= 1)