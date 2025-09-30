"""Teacher-related scheduling restrictions as classes."""

from restrictions import Restriction


class TeacherOneClassAtATime(Restriction):
    """Restricts each teacher to teach at most one class in each time slot."""

    def apply(self, model, assignments, teachers, num_days, num_hours):
        for teacher in teachers:
            for d in range(num_days):
                for h in range(num_hours):
                    model.AddAtMostOne(assignments[key] for key in assignments if key[2] == teacher.id and key[3] == d and key[4] == h)


class TeacherMaxWeeklyHours(Restriction):
    """Restrict each teacher to not exceed their maximum weekly hours."""

    def apply(self, model, assignments, teachers):
        for teacher in teachers:
            max_hours = teacher.max_hours_week
            # Sum of all assignment vars for this teacher across days/hours
            total = sum(assignments[key] for key in assignments if key[2] == teacher.id)
            model.Add(total <= max_hours)
