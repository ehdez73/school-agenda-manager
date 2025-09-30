"""Enforce teacher unavailable times from stored preferences.

This restriction reads the JSON-encoded `preferences` field on each Teacher
and looks for a mapping day -> {"unavailable": [...], "preferred": [...] }.
For each unavailable hour on a given day it adds a constraint forcing the sum
of assignment variables for that teacher at that day+hour to be 0 (i.e. no
assignment may be given).

The implementation is defensive: invalid JSON, missing keys or out-of-range
hour indices are ignored.
"""

import json

from .base import Restriction


class TeacherUnavailableTimes(Restriction):
    """Prevent assigning teachers to hours they marked as unavailable.

    apply(model, assignments, teachers, num_days, num_hours)
    """

    def apply(self, model, assignments, teachers, num_days, num_hours):
        for teacher in teachers:
            prefs_raw = getattr(teacher, 'preferences', None)
            if not prefs_raw:
                continue

            # preferences are stored as a JSON string in the DB routes
            try:
                prefs = json.loads(prefs_raw) if isinstance(prefs_raw, str) else prefs_raw
            except Exception:
                # malformed preferences; skip this teacher
                continue

            if not isinstance(prefs, dict):
                continue

            # For each weekday index, find matching key in preferences.
            for d in range(num_days):
                # Preferences use numeric keys for day indices
                entry = prefs.get(str(d)) or prefs.get(d)
                if not entry:
                    continue

                unavailable = entry.get('unavailable', [])

                # Normalize and deduplicate hours
                try:
                    hours = sorted({int(x) for x in unavailable})
                except Exception:
                    # If conversion fails, skip
                    continue

                for h in hours:
                    if h < 0 or h >= num_hours:
                        # out of range hour index; ignore
                        continue

                    # Collect all assignment vars for this teacher at day d and hour h
                    vars_for_slot = [assignments[key] for key in assignments
                                     if key[2] == teacher.id and key[3] == d and key[4] == h]
                    if not vars_for_slot:
                        continue

                    # Force none of the vars to be selected at this timeslot
                    model.Add(sum(vars_for_slot) == 0)
