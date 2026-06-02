"""Subject weekly hours restriction: ensure each subject gets its required weekly hours."""

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


class SubjectWeeklyHours(Restriction):
    """Ensure each subject gets its required weekly hours for each group."""

    def apply(self, model, assignments, all_groups, all_subjects):
        self._apply_impl(model, assignments, all_groups, all_subjects)

    def apply_with_assumptions(self, model, assignments, all_groups, all_subjects):
        return self._apply_impl(model, assignments, all_groups, all_subjects,
                                diagnostic_mode=True)

    def _apply_impl(self, model, assignments, all_groups, all_subjects,
                    diagnostic_mode=False):
        assumptions = []
        for group in all_groups:
            course, line_letter = group.split('-')
            line_index = ord(line_letter) - ord('A')
            for subject in all_subjects:
                if subject.course_id != course:
                    continue
                if not _is_line_included(subject, line_index):
                    continue
                # Sum all assignments for this group-subject combination
                hours = sum(assignments[key] for key in assignments
                            if key[0] == group and key[1] == subject.id)
                if diagnostic_mode:
                    assume = model.NewBoolVar(
                        f"assume_weekly_{group}_{subject.id}")
                    model.Add(hours == subject.weekly_hours).OnlyEnforceIf(assume)
                    assumptions.append((assume, {
                        "restriction": "SubjectWeeklyHours",
                        "entity_type": "subject",
                        "entity_id": subject.id,
                        "entity_name": subject.name,
                        "extra": {"group": group,
                                  "weekly_hours": subject.weekly_hours},
                    }))
                else:
                    # Add constraint: must match required weekly hours
                    model.Add(hours == subject.weekly_hours)
        return assumptions
