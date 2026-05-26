"""Ensure teachers do not exceed their weekly maximum teaching hours."""

from .base import Restriction


class TeacherMaxWeeklyHours(Restriction):
    """Restrict each teacher to not exceed their maximum weekly hours."""

    def apply(self, model, assignments, teachers):
        self._apply_impl(model, assignments, teachers)

    def apply_with_assumptions(self, model, assignments, teachers):
        return self._apply_impl(model, assignments, teachers, diagnostic_mode=True)

    def _apply_impl(self, model, assignments, teachers, diagnostic_mode=False):
        assumptions = []
        for teacher in teachers:
            max_hours = teacher.max_hours_week
            # Sum of all assignment vars for this teacher across days/hours
            total = sum(assignments[key] for key in assignments if key[2] == teacher.id)
            if diagnostic_mode:
                assume = model.NewBoolVar(f"assume_maxh_{teacher.id}")
                model.Add(total <= max_hours).OnlyEnforceIf(assume)
                assumptions.append((assume, {
                    "restriction": "TeacherMaxWeeklyHours",
                    "entity_type": "teacher",
                    "entity_id": teacher.id,
                    "entity_name": teacher.name,
                    "extra": {"max_hours_week": max_hours},
                }))
            else:
                model.Add(total <= max_hours)
        return assumptions
