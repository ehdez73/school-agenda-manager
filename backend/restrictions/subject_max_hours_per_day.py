from ortools.sat.python import cp_model
from .base import Restriction

class SubjectMaxHoursPerDay(Restriction):
    """
    Restriction to ensure that a subject is not scheduled for more than `max_hours_per_day` in a single day.
    This applies both to direct assignments and assignments through SubjectGroups.
    """

    def apply(self, model, assignments, subjects, subject_groups):
        """
        Apply the restriction to the CP-SAT model.

        Args:
            model (cp_model.CpModel): The constraint programming model.
            assignments (dict): A dictionary mapping (group, subject_id, teacher_id, day, hour) to BoolVars.
            subjects (list[Subject]): List of Subject objects.
            subject_groups (list[SubjectGroup]): List of SubjectGroup objects.
        """
        for subject in subjects:
            max_hours = subject.max_hours_per_day

            # Debug: Log subject details
            print(f"Applying max hours per day restriction for subject: {subject.id}, max_hours: {max_hours}")

            # Collect all variables for this subject per day
            for day in range(5):  # Assuming 5 days (Monday to Friday)
                daily_vars = []

                for (group, subject_id, teacher_id, d, hour), var in assignments.items():
                    if subject_id == subject.id and d == day:
                        daily_vars.append(var)

                # Debug: Log daily variables
                print(f"Day {day}, daily_vars: {[str(var) for var in daily_vars]}")

                # Add the constraint to limit daily hours
                if daily_vars:
                    model.Add(sum(daily_vars) <= max_hours)
                    print(f"Constraint added: sum(daily_vars) <= {max_hours}")