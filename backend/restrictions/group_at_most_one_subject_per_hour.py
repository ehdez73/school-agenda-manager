"""Ensure a group has at most one subject assigned in any given day/hour, except for SubjectGroups."""

from .base import Restriction


class GroupAtMostOneSubjectPerHour(Restriction):
    """Ensure a group has at most one subject assigned in any given day/hour,
    unless those subjects belong to the same SubjectGroup (in which case all
    subjects from that group should be assigned together).
    """

    def apply(self, model, assignments, groups, num_days, num_hours, all_subjectgroups=None):
        # Build mapping to identify which subjects belong to the same SubjectGroup
        subject_to_groups = {}
        if all_subjectgroups:
            for sg in all_subjectgroups:
                # Handle both real SubjectGroup models and test schemas
                if hasattr(sg, 'subjects') and sg.subjects:
                    subject_ids = [s.id for s in sg.subjects]  # Real model with relationship
                elif hasattr(sg, 'subject_ids') and sg.subject_ids:
                    subject_ids = sg.subject_ids  # Test schema with direct IDs
                else:
                    subject_ids = []
                
                for subject_id in subject_ids:
                    if subject_id not in subject_to_groups:
                        subject_to_groups[subject_id] = []
                    subject_to_groups[subject_id].append(sg.id)

        for group in groups:
            for d in range(num_days):
                for h in range(num_hours):
                    # Get all assignments for this group/day/hour
                    slot_assignments = [
                        k for k in assignments
                        if k[0] == group and k[3] == d and k[4] == h
                    ]
                    
                    if not slot_assignments:
                        continue
                    
                    # Group assignments by their SubjectGroup membership
                    grouped_assignments = {}  # subjectgroup_id -> list of assignment keys
                    standalone_assignments = []  # assignments for subjects not in any group
                    
                    for k in slot_assignments:
                        subject_id = k[1]
                        if subject_id in subject_to_groups:
                            # This subject belongs to one or more SubjectGroups
                            for sg_id in subject_to_groups[subject_id]:
                                if sg_id not in grouped_assignments:
                                    grouped_assignments[sg_id] = []
                                grouped_assignments[sg_id].append(k)
                        else:
                            # This subject doesn't belong to any SubjectGroup
                            standalone_assignments.append(k)
                    
                    # Count constraint groups:
                    # 1. Each SubjectGroup counts as one "logical assignment"
                    # 2. Each standalone subject counts as one "logical assignment"
                    # Total logical assignments should be <= 1
                    
                    logical_groups = []
                    
                    # Add SubjectGroup logical assignments
                    for sg_id, sg_assignments in grouped_assignments.items():
                        if sg_assignments:
                            # All subjects in a SubjectGroup are treated as one logical unit
                            # If any subject from the group is assigned, count it as 1
                            logical_groups.append(sum(assignments[k] for k in sg_assignments))
                    
                    # Add standalone subject logical assignments
                    for k in standalone_assignments:
                        logical_groups.append(assignments[k])
                    
                    # At most one logical group can be active
                    if len(logical_groups) > 1:
                        model.Add(sum(logical_groups) <= 1)
