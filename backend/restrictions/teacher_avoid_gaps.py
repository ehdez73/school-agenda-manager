"""Soft constraint: reward schedules where each teacher's daily hours
are in a single contiguous block (no gaps between classes).

This adds penalty terms to the objective when a teacher has empty hours
between non-empty hours on the same day. Gaps at the beginning or end of
the day are not penalized — only gaps *between* busy hours.
"""

from .base import Restriction


class TeacherAvoidGaps(Restriction):
    """Soft constraint: reward schedules where each teacher's daily hours
    form a single contiguous block (no gaps).

    apply(model, assignments, teachers, num_days, num_hours)
    """

    def __init__(self, weight: int = 10):
        self.weight = weight
        self.preference_terms = []

    def apply(self, model, assignments, teachers, num_days, num_hours):
        self.preference_terms = []

        for teacher in teachers:
            for d in range(num_days):
                busy = []
                for h in range(num_hours):
                    b = model.NewBoolVar(f"b_t{teacher.id}_d{d}_h{h}")
                    slot_vars = [
                        assignments[k]
                        for k in assignments
                        if k[2] == teacher.id and k[3] == d and k[4] == h
                    ]
                    if slot_vars:
                        # A joint class can activate more than one assignment var
                        # for the same teacher/day/hour (one per group line).
                        # Channel b as "teacher is busy at this slot" instead of
                        # forcing equality with the raw sum.
                        model.Add(b <= sum(slot_vars))
                        model.Add(sum(slot_vars) <= len(slot_vars) * b)
                    else:
                        model.Add(b == 0)
                    busy.append(b)

                starts = []
                for h in range(num_hours):
                    s = model.NewBoolVar(f"s_t{teacher.id}_d{d}_h{h}")
                    if h == 0:
                        model.Add(s == busy[h])
                    else:
                        model.Add(s >= busy[h] - busy[h-1])
                        model.Add(s <= busy[h])
                        model.Add(s <= 1 - busy[h-1])
                    starts.append(s)

                total_starts = sum(starts)

                excess = model.NewIntVar(
                    0, num_hours,
                    f"excess_t{teacher.id}_d{d}",
                )
                model.Add(excess >= total_starts - 1)
                model.Add(excess >= 0)

                self.preference_terms.append(-self.weight * excess)
