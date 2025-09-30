from .base import Restriction

class TeacherOneSubjectPerGroup(Restriction):
    """
    Restriction to ensure that if a teacher teaches a subject to a group, no other teacher can teach the same subject to that group.
    """

    def apply(self, model, assignments, teachers, groups, subjects):
        """
        Apply the restriction to the CP-SAT model.

        Args:
            model (cp_model.CpModel): The constraint programming model.
            assignments (dict): A dictionary mapping (group, subject_id, teacher_id, day, hour) to BoolVars.
            teachers (list[Teacher]): List of Teacher objects.
            groups (list[str]): List of group identifiers.
            subjects (list[Subject]): List of Subject objects.
        """
        for group in groups:
            for subject in subjects:
                # Collect all variables for this group and subject
                teacher_vars = [
                    assignments[(group, subject.id, teacher.id, day, hour)]
                    for teacher in teachers
                    for day in range(5)  # Assuming 5 days (Monday to Friday)
                    for hour in range(5)  # Assuming 5 hours per day
                    if (group, subject.id, teacher.id, day, hour) in assignments
                ]

                # Ensure at most one teacher is assigned to this subject for the group
                model.Add(sum(teacher_vars) <= 1)