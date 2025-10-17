"""Encourage tutors to teach subjects in their assigned tutor group.

This soft restriction rewards assignments where a teacher who is assigned as a tutor
for a group teaches subjects in that same group, prioritizing them over other teachers.
"""

from .base import Restriction


def normalize_group_name(group: str) -> str:
    """
    Normalize group names to ensure consistency.
    Handles both formats:
    - "1ºA" (no dash) -> "1º-A"
    - "1º-A" (with dash) -> "1º-A"

    Args:
        group: Group identifier

    Returns:
        Normalized group identifier with dash before last character
    """
    if not group:
        return group

    # If it already has a dash, return as-is
    if "-" in group:
        return group

    # If no dash, add one before the last character
    # e.g., "1ºA" -> "1º-A"
    if len(group) > 1:
        return f"{group[:-1]}-{group[-1]}"

    return group


class TutorPreference(Restriction):
    """Soft constraint encouraging tutors to teach in their assigned group."""

    def __init__(self, weight: int = 10):
        """
        Initialize the tutor preference restriction.

        Args:
            weight: Weight for the preference term in the objective function.
                   Higher values give more priority to tutor assignments.
        """
        self.weight = weight
        self.preference_terms = []

    def apply(self, model, assignments, teachers):
        """
        Apply tutor preference constraints to the model.

        Args:
            model: CP-SAT model to add constraints to.
            assignments: Dictionary of decision variables keyed by
                        (group, subject_id, teacher_id, day, hour).
            teachers: List of all teachers.
        """
        self.preference_terms = []

        for teacher in teachers:
            # Check if this teacher has an assigned tutor group
            tutor_group = getattr(teacher, "tutor_group", None)
            if not tutor_group:
                continue

            # Normalize the tutor_group to match scheduler format
            normalized_tutor_group = normalize_group_name(tutor_group)

            # Collect all assignments where this teacher teaches in their tutor group
            tutor_group_assignments = [
                assignments[key]
                for key in assignments
                if key[0] == normalized_tutor_group and key[2] == teacher.id
            ]

            if not tutor_group_assignments:
                continue

            # Add preference terms (sum of all assignments for this tutor in their group)
            expr = sum(tutor_group_assignments)
            if self.weight != 1:
                self.preference_terms.append(self.weight * expr)
            else:
                self.preference_terms.append(expr)
