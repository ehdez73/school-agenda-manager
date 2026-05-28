"""Enforce SubjectGroup constraints: subjects in the same group must be assigned together."""

import json as _json

from .base import Restriction


def _is_line_included(entity, line_index):
    """Check whether a SubjectGroup applies to the given line index.

    Args:
        entity: SubjectGroup with optional included_lines attribute.
        line_index: Integer line index (0 = A, 1 = B, etc.).

    Returns:
        True if the entity applies to this line (included or included_lines is None).
    """
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


class SubjectGroupAssignment(Restriction):
    """Manages SubjectGroup assignments:

    1. When any subject from a SubjectGroup is assigned to a timeslot,
       ALL subjects from that group must be assigned to the same timeslot.
    2. This allows multiple subjects to share a timeslot only if they belong
       to the same SubjectGroup (like VAL/REL).

    The assignments dict is keyed as (group, subject_id, teacher_id, day, hour).
    """

    def apply(self, model, assignments, all_groups, all_subjects, all_subjectgroups):
        # For each SubjectGroup, ensure all subjects are assigned together
        for sg in all_subjectgroups:
            # Handle both real SubjectGroup models and test schemas
            if hasattr(sg, 'subjects') and sg.subjects:
                subject_ids = [s.id for s in sg.subjects]  # Real model with relationship
            elif hasattr(sg, 'subject_ids') and sg.subject_ids:
                subject_ids = sg.subject_ids  # Test schema with direct IDs
            else:
                subject_ids = []

            if len(subject_ids) < 2:  # Skip groups with less than 2 subjects
                continue

            for group in all_groups:
                # Respect included_lines on the SubjectGroup
                _, line_letter = group.split("-")
                line_index = ord(line_letter) - ord("A")
                if not _is_line_included(sg, line_index):
                    continue

                # Get all day/hour combinations for this group
                hours = set((k[3], k[4]) for k in assignments if k[0] == group)
                for (day, hour) in hours:
                    # For each pair of subjects in the SubjectGroup,
                    # ensure they are assigned together (both or neither)
                    for i in range(len(subject_ids)):
                        for j in range(i + 1, len(subject_ids)):
                            subj1_id = subject_ids[i]
                            subj2_id = subject_ids[j]

                            # Get all possible assignments for each subject at this timeslot
                            subj1_vars = [
                                assignments[k]
                                for k in assignments
                                if k[0] == group and k[1] == subj1_id and k[3] == day and k[4] == hour
                            ]
                            subj2_vars = [
                                assignments[k]
                                for k in assignments
                                if k[0] == group and k[1] == subj2_id and k[3] == day and k[4] == hour
                            ]

                            # Ensure both subjects have the same assignment status
                            # sum(subj1_vars) == sum(subj2_vars)
                            if subj1_vars and subj2_vars:
                                model.Add(sum(subj1_vars) == sum(subj2_vars))
