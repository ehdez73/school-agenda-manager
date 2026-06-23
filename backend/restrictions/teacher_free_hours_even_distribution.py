"""Soft constraint: reward schedules where each teacher's free/unassigned
hours are evenly distributed across the week."""
from .base import Restriction


class TeacherFreeHoursEvenDistribution(Restriction):
    def __init__(self, weight: int = 30):
        self.weight = weight
        self.preference_terms = []

    def apply(self, model, assignments, teachers, num_days, num_hours):
        self.preference_terms = []
        for teacher in teachers:
            free_vars = []
            for d in range(num_days):
                busy = []
                for h in range(num_hours):
                    b = model.NewBoolVar(f"fb_t{teacher.id}_d{d}_h{h}")
                    slot_vars = [
                        assignments[k]
                        for k in assignments
                        if k[2] == teacher.id and k[3] == d and k[4] == h
                    ]
                    if slot_vars:
                        model.Add(b <= sum(slot_vars))
                        model.Add(sum(slot_vars) <= len(slot_vars) * b)
                    else:
                        model.Add(b == 0)
                    busy.append(b)

                free_h = model.NewIntVar(0, num_hours, f"free_t{teacher.id}_d{d}")
                model.Add(free_h == num_hours - sum(busy))
                free_vars.append(free_h)

            max_free = model.NewIntVar(0, num_hours, f"max_free_t{teacher.id}")
            min_free = model.NewIntVar(0, num_hours, f"min_free_t{teacher.id}")
            model.AddMaxEquality(max_free, free_vars)
            model.AddMinEquality(min_free, free_vars)

            spread = model.NewIntVar(0, num_hours, f"spread_t{teacher.id}")
            model.Add(spread == max_free - min_free)

            self.preference_terms.append(-self.weight * spread)
