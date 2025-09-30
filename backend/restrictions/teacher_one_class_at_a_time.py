"""Teacher-related restriction: a teacher can teach at most one class per timeslot."""

from .base import Restriction


class TeacherOneClassAtATime(Restriction):
    """Restricts each teacher to teach at most one class in each time slot."""

    def apply(self, model, assignments, teachers, num_days, num_hours):
        for teacher in teachers:
            for d in range(num_days):
                for h in range(num_hours):
                    model.AddAtMostOne(assignments[key] for key in assignments if key[2] == teacher.id and key[3] == d and key[4] == h)
