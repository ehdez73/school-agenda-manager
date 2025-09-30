"""Encourage scheduling teachers in their preferred timeslots.

This soft restriction reads the JSON-encoded preferences for each teacher and
collects objective terms that reward assignments falling within preferred
hours. Invalid data is ignored so it never blocks the solver.
"""

import json

from .base import Restriction

WEEKDAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]  # For backward compatibility


class TeacherPreferredTimes(Restriction):
    """Soft constraint encouraging assignments in teacher preferred slots."""

    def __init__(self, weight: int = 1):
        self.weight = weight
        self.preference_terms = []

    def apply(self, model, assignments, teachers, num_days, num_hours):
        self.preference_terms = []
        seen_slots = set()

        for teacher in teachers:
            prefs_raw = getattr(teacher, "preferences", None)
            if not prefs_raw:
                continue

            try:
                prefs = json.loads(prefs_raw) if isinstance(prefs_raw, str) else prefs_raw
            except Exception:
                continue

            if not isinstance(prefs, dict):
                continue

            for d in range(num_days):
                weekday_name = WEEKDAYS[d] if d < len(WEEKDAYS) else str(d)

                entry = None
                if str(d) in prefs:
                    entry = prefs.get(str(d))
                elif d in prefs:
                    entry = prefs.get(d)
                else:
                    matched_key = None
                    for k in prefs.keys():
                        try:
                            if str(k).strip().lower() == str(weekday_name).strip().lower():
                                matched_key = k
                                break
                        except Exception:
                            continue
                    if matched_key is None:
                        continue
                    entry = prefs.get(matched_key, {}) or {}

                if not isinstance(entry, dict):
                    continue

                preferred = entry.get("preferred", [])
                if not preferred:
                    continue

                try:
                    hours = sorted({int(x) for x in preferred})
                except Exception:
                    continue

                for h in hours:
                    if h < 0 or h >= num_hours:
                        continue

                    slot_key = (teacher.id, d, h)
                    if slot_key in seen_slots:
                        continue

                    vars_for_slot = [
                        assignments[key]
                        for key in assignments
                        if key[2] == teacher.id and key[3] == d and key[4] == h
                    ]
                    if not vars_for_slot:
                        continue

                    seen_slots.add(slot_key)
                    expr = sum(vars_for_slot)
                    if self.weight != 1:
                        self.preference_terms.append(self.weight * expr)
                    else:
                        self.preference_terms.append(expr)
