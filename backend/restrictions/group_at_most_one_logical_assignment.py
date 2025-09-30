"""Ensure at most one logical assignment per group/day/hour, respecting SubjectGroups."""

from .base import Restriction


class GroupAtMostOneLogicalAssignment(Restriction):
    """Ensure at most one logical assignment per group/day/hour.
    
    A logical assignment is either:
    - One standalone subject (not in any SubjectGroup)
    - One complete SubjectGroup (all its subjects together)
    """

    def apply(self, model, assignments, all_groups, num_days, num_hours, all_subjectgroups=None):
        # Build mapping to identify which subjects belong to SubjectGroups
        subjects_in_groups = set()
        sg_subject_map = {}  # subject_id -> subjectgroup_id
        
        if all_subjectgroups:
            for sg in all_subjectgroups:
                # Handle both real SubjectGroup models and test schemas
                if hasattr(sg, 'subjects') and sg.subjects:
                    subject_ids = [s.id for s in sg.subjects]
                elif hasattr(sg, 'subject_ids') and sg.subject_ids:
                    subject_ids = sg.subject_ids
                else:
                    subject_ids = []
                
                if len(subject_ids) > 1:  # Only care about groups with multiple subjects
                    for subject_id in subject_ids:
                        subjects_in_groups.add(subject_id)
                        sg_subject_map[subject_id] = sg.id

        for group in all_groups:
            for d in range(num_days):
                for h in range(num_hours):
                    # Get all assignments for this timeslot
                    slot_assignments = [
                        k for k in assignments
                        if k[0] == group and k[3] == d and k[4] == h
                    ]
                    
                    if not slot_assignments:
                        continue
                    
                    # Group assignments by their logical unit
                    logical_units = {}  # unit_id -> list of assignment keys
                    
                    for k in slot_assignments:
                        subject_id = k[1]
                        
                        if subject_id in subjects_in_groups:
                            # This subject belongs to a SubjectGroup - use the group ID as unit
                            unit_id = f"subjectgroup_{sg_subject_map[subject_id]}"
                        else:
                            # Standalone subject - each gets its own unit
                            unit_id = f"standalone_{subject_id}"
                        
                        if unit_id not in logical_units:
                            logical_units[unit_id] = []
                        logical_units[unit_id].append(k)
                    
                    # Create logical unit variables
                    logical_vars = []
                    for unit_id, unit_assignments in logical_units.items():
                        if unit_assignments:
                            # A logical unit is active if any of its assignments is active
                            unit_vars = [assignments[k] for k in unit_assignments]
                            if len(unit_vars) == 1:
                                logical_vars.append(unit_vars[0])
                            else:
                                # Create auxiliary variable for this logical unit
                                unit_var = model.NewBoolVar(f"logical_unit_{group}_{d}_{h}_{unit_id}")
                                # unit_var == 1 iff any assignment in this unit is active
                                model.Add(unit_var <= sum(unit_vars))
                                model.Add(sum(unit_vars) <= len(unit_vars) * unit_var)
                                logical_vars.append(unit_var)
                    
                    # At most one logical unit can be active per timeslot
                    if len(logical_vars) > 1:
                        model.Add(sum(logical_vars) <= 1)