import json as _json
from collections import defaultdict
import logging
import time

from ortools.sat.python import cp_model
from .models import (
    Teacher,
    Subject,
    Course,
    Config,
    Timeslot,
    TimeSlotAssignment,
    SubjectGroup,
)
from .logging_config import build_log_extra


logger = logging.getLogger(__name__)


def _is_line_included(entity, line_index):
    """Check whether a Subject or SubjectGroup applies to the given line index.
    
    Args:
        entity: Subject or SubjectGroup instance with optional included_lines attribute.
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

from .restrictions import (
    SubjectWeeklyHours,
    TeacherOneClassAtATime,
    TeacherMaxWeeklyHours,
    GroupSubjectMaxHoursPerDay,
    GroupAtMostOneLogicalAssignment,
    SubjectGroupAssignment,
    TeacherUnavailableTimes,
    TeacherPreferredTimes,
    TutorPreference,
    TutorMandatoryHours,
    GroupSubjectHoursMustBeConsecutive,
    GroupSubjectHoursMustNotBeConsecutive,
    SubjectMustEveryDay,
    LinkedSubjectsConsecutive,
)


def save_solution_to_db(session, solver, assignments, groups, num_days, num_hours, task_id=None):
    logger.info(
        "Persisting timetable solution groups=%d days=%d hours=%d",
        len(groups),
        num_days,
        num_hours,
        extra=build_log_extra(task_id=task_id),
    )
    assignment_count = 0
    timeslot_count = 0

    try:
        # Clear previous schedule
        session.query(TimeSlotAssignment).delete()
        session.query(Timeslot).delete()
        session.commit()
        logger.debug("Cleared previous timetable data", extra=build_log_extra(task_id=task_id))

        for d in range(num_days):
            for h in range(num_hours):
                for group in groups:
                    course_id, line_str = group.split("-")
                    line_num = ord(line_str) - ord("A")

                    # store day as integer index `d` (0 = first weekday)
                    timeslot = Timeslot(day=d, hour=h, course_id=course_id, line=line_num)
                    session.add(timeslot)
                    timeslot_count += 1

                    for key in assignments:
                        if (
                            key[0] == group
                            and key[3] == d
                            and key[4] == h
                            and solver.Value(assignments[key]) == 1
                        ):
                            _, subject_id, teacher_id, _, _ = key
                            assignment = TimeSlotAssignment(
                                timeslot=timeslot,
                                subject_id=subject_id,
                                teacher_id=teacher_id,
                            )
                            session.add(assignment)
                            assignment_count += 1

        session.commit()
        logger.info(
            "Timetable persisted successfully timeslots=%d assignments=%d",
            timeslot_count,
            assignment_count,
            extra=build_log_extra(task_id=task_id),
        )
    except Exception:
        session.rollback()
        logger.exception("Failed to persist timetable solution", extra=build_log_extra(task_id=task_id))
        raise


def _create_assignments(model, all_teachers, all_subjects, all_groups, num_days, num_hours):
    """Create decision variables (group, subject_id, teacher_id, day, hour)."""
    assignments = {}
    for group in all_groups:
        course, line_letter = group.split("-")
        line_index = ord(line_letter) - ord("A")
        for subject in all_subjects:
            if subject.course_id == course and _is_line_included(subject, line_index):
                for teacher in all_teachers:
                    if subject in teacher.subjects:
                        for d in range(num_days):
                            for h in range(num_hours):
                                key = (group, subject.id, teacher.id, d, h)
                                assignments[key] = model.NewBoolVar(
                                    f"g:{group} sub:{subject.id} t:{teacher.name} d:{d} h:{h}"
                                )
    return assignments


def _build_hard_restrictions(model, assignments, all_teachers, all_subjects,
                             all_groups, all_subjectgroups, num_days, num_hours):
    """Build the list of (name, restriction_instance, args) for all hard restrictions."""
    return [
        ("SubjectWeeklyHours", SubjectWeeklyHours(), [model, assignments, all_groups, all_subjects]),
        ("TeacherOneClassAtATime", TeacherOneClassAtATime(), [model, assignments, all_teachers, num_days, num_hours]),
        ("TeacherUnavailableTimes", TeacherUnavailableTimes(), [model, assignments, all_teachers, num_days, num_hours]),
        ("TeacherMaxWeeklyHours", TeacherMaxWeeklyHours(), [model, assignments, all_teachers]),
        ("GroupSubjectMaxHoursPerDay", GroupSubjectMaxHoursPerDay(), [model, assignments, all_groups, all_subjects, all_teachers, num_days]),
        ("GroupAtMostOneLogicalAssignment", GroupAtMostOneLogicalAssignment(), [model, assignments, all_groups, num_days, num_hours, all_subjectgroups]),
        ("GroupSubjectHoursMustBeConsecutive", GroupSubjectHoursMustBeConsecutive(), [model, assignments, all_groups, [s for s in all_subjects if getattr(s, "consecutive_hours", True)], num_days, num_hours]),
        ("GroupSubjectHoursMustNotBeConsecutive", GroupSubjectHoursMustNotBeConsecutive(), [model, assignments, all_groups, [s for s in all_subjects if not getattr(s, "consecutive_hours", True)], num_days, num_hours]),
        ("LinkedSubjectsConsecutive", LinkedSubjectsConsecutive(), [model, assignments, all_groups, all_subjects, num_days, num_hours]),
        ("SubjectGroupAssignment", SubjectGroupAssignment(), [model, assignments, all_groups, all_subjects, all_subjectgroups]),
        ("SubjectMustEveryDay", SubjectMustEveryDay(), [model, assignments, all_groups, all_subjects, num_days]),
    ]


def _build_soft_restrictions(model, assignments, all_teachers,
                              all_subjectgroups, num_days, num_hours):
    """Build the list of (name, restriction_instance, args) for all soft restrictions."""
    return [
        ("TeacherPreferredTimes", TeacherPreferredTimes(),
         [model, assignments, all_teachers, num_days, num_hours]),
        ("TutorPreference", TutorPreference(weight=100),
         [model, assignments, all_teachers]),
        ("TutorMandatoryHours", TutorMandatoryHours(weight=500),
         [model, assignments, all_teachers, num_days, num_hours, all_subjectgroups]),
    ]


def solve_scheduling_model(
    all_teachers, all_subjects, all_groups, all_subjectgroups, num_days, num_hours,
    skip_restrictions=None, diagnostic_mode=False, task_id=None,
):
    """
    Builds and solves the scheduling model without requiring a database session.

    Args:
        all_teachers: List of Teacher objects
        all_subjects: List of Subject objects
        all_groups: List of group identifiers (e.g., "1-A", "1-B")
        all_subjectgroups: List of SubjectGroup objects
        num_days: Number of days per week
        num_hours: Number of hours per day
        skip_restrictions: Set of restriction class names to skip (optional)
        diagnostic_mode: If True, use shorter timeout (default: False)

    Returns:
        Tuple of (status, assignments, solver) where:
        - status: CP-SAT solver status (OPTIMAL, FEASIBLE, or INFEASIBLE)
        - assignments: Dictionary of decision variables
        - solver: The solver object with the solution
    """
    # --- 1. Model Initialization ---
    model = cp_model.CpModel()
    if skip_restrictions is None:
        skip_restrictions = set()
    logger.info(
        "Building scheduling model teachers=%d subjects=%d groups=%d days=%d hours=%d diagnostic_mode=%s skipped=%d",
        len(all_teachers),
        len(all_subjects),
        len(all_groups),
        num_days,
        num_hours,
        diagnostic_mode,
        len(skip_restrictions),
        extra=build_log_extra(task_id=task_id),
    )

    # Create decision variables (group-subject-teacher-day-hour)
    assignments = _create_assignments(model, all_teachers, all_subjects, all_groups, num_days, num_hours)
    logger.debug(
        "Created assignment decision variables count=%d",
        len(assignments),
        extra=build_log_extra(task_id=task_id),
    )

    # Pre-solve validation: run all sanity checks before building constraints
    sanity_issues = _run_sanity_checks(
        all_teachers, all_subjects, all_groups,
        all_subjectgroups, num_days, num_hours,
    )
    if sanity_issues:
        for issue in sanity_issues:
            logger.warning("Sanity issue: %s", issue, extra=build_log_extra(task_id=task_id))
        logger.warning(
            "Data sanity check failed count=%d",
            len(sanity_issues),
            extra=build_log_extra(task_id=task_id),
        )
        return cp_model.INFEASIBLE, assignments, cp_model.CpSolver()

    # Hard restrictions
    hard_restrictions = _build_hard_restrictions(
        model, assignments, all_teachers, all_subjects,
        all_groups, all_subjectgroups, num_days, num_hours,
    )
    hard_applied = 0
    hard_skipped = 0
    for name, restriction, args in hard_restrictions:
        if name not in skip_restrictions:
            logger.debug("Applying hard restriction=%s", name, extra=build_log_extra(task_id=task_id))
            restriction.apply(*args)
            hard_applied += 1
        else:
            hard_skipped += 1
            logger.debug("Skipping hard restriction=%s", name, extra=build_log_extra(task_id=task_id))

    # Soft constraints (preferences) — never cause infeasibility on their own
    soft_restrictions = _build_soft_restrictions(
        model, assignments, all_teachers,
        all_subjectgroups, num_days, num_hours,
    )
    preference_terms = []
    soft_applied = 0
    soft_skipped = 0
    for name, restriction, args in soft_restrictions:
        if name not in skip_restrictions:
            logger.debug("Applying soft restriction=%s", name, extra=build_log_extra(task_id=task_id))
            restriction.apply(*args)
            preference_terms.extend(restriction.preference_terms)
            soft_applied += 1
        else:
            soft_skipped += 1
            logger.debug("Skipping soft restriction=%s", name, extra=build_log_extra(task_id=task_id))
    if preference_terms:
        model.Maximize(sum(preference_terms))
    logger.info(
        "Restrictions prepared hard_applied=%d hard_skipped=%d soft_applied=%d soft_skipped=%d preference_terms=%d",
        hard_applied,
        hard_skipped,
        soft_applied,
        soft_skipped,
        len(preference_terms),
        extra=build_log_extra(task_id=task_id),
    )

    # --- 2. Solve ---
    logger.info("Starting CP-SAT solver", extra=build_log_extra(task_id=task_id))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0 if diagnostic_mode else 60.0
    started_at = time.perf_counter()
    status = solver.Solve(model)
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "Solver finished status=%s elapsed_ms=%.2f timeout_seconds=%.1f",
        solver.StatusName(status),
        elapsed_ms,
        solver.parameters.max_time_in_seconds,
        extra=build_log_extra(task_id=task_id),
    )

    return status, assignments, solver


def _get_line_index(group):
    """Extract the line index (0=A, 1=B, ...) from a group identifier."""
    _, line_letter = group.split("-")
    return ord(line_letter) - ord("A")


def _check_capacity_sanity(all_subjects, all_groups, num_days, num_hours, all_subjectgroups):
    """Quick capacity sanity checks before running the solver.

    Subjects within a SubjectGroup share the same physical timeslots,
    so their overlapping hours are counted only once.

    Returns a list of issue descriptions (empty list = all clear).
    """
    subject_ids_in_groups = {}
    for sg in all_subjectgroups:
        for s in sg.subjects:
            subject_ids_in_groups[s.id] = sg

    issues = []
    for group in all_groups:
        course = group.split("-")[0]
        line_index = _get_line_index(group)

        standalone_hours = sum(
            s.weekly_hours for s in all_subjects
            if s.course_id == course
            and s.id not in subject_ids_in_groups
            and _is_line_included(s, line_index)
        )
        grouped_hours = 0
        for sg in all_subjectgroups:
            if not _is_line_included(sg, line_index):
                continue
            group_subjects = [s for s in sg.subjects if s.course_id == course and _is_line_included(s, line_index)]
            if group_subjects:
                grouped_hours += max(s.weekly_hours for s in group_subjects)

        required = standalone_hours + grouped_hours
        available = num_days * num_hours
        if required > available:
            issues.append(
                f"  - **Group {group}**: requires {required}h/week but only "
                f"{available} slots available ({num_days} days × {num_hours} hours). "
                f"Possible cause: **SubjectWeeklyHours**."
            )
    return issues


def _check_subjects_without_teachers(all_subjects, all_teachers, all_groups,
                                     all_subjectgroups):
    """Check that every subject has at least one teacher who can teach it.

    Subjects within a SubjectGroup still need at least one teacher each.

    Returns a list of issue descriptions (empty list = all clear).
    """
    subjects_with_teachers = set()
    for teacher in all_teachers:
        for subject in getattr(teacher, 'subjects', []):
            subjects_with_teachers.add(subject.id)

    issues = []
    for group in all_groups:
        course = group.split("-")[0]
        line_index = _get_line_index(group)
        for subject in all_subjects:
            if (subject.course_id == course
                    and _is_line_included(subject, line_index)
                    and subject.id not in subjects_with_teachers):
                issues.append(
                    f"  - **Subject \"{subject.name}\" (id={subject.id})** "
                    f"in **Group {group}** has no teacher assigned."
                )
    return issues


def _check_subjectgroup_weekly_hours_consistency(all_subjectgroups):
    """Check all SubjectGroup members have identical weekly_hours."""
    issues = []
    for sg in all_subjectgroups:
        subjects_list = getattr(sg, 'subjects', [])
        if not subjects_list or len(subjects_list) < 2:
            continue
        hours = {s.weekly_hours for s in subjects_list}
        if len(hours) > 1:
            names = [f"{s.name}({s.weekly_hours}h)" for s in subjects_list]
            sg_name = getattr(sg, 'name', None) or getattr(sg, 'id', 'unknown')
            issues.append(
                f"  - **SubjectGroup \"{sg_name}\"**: members have different "
                f"weekly_hours: {', '.join(names)}. "
                f"All subjects in a SubjectGroup must have the same weekly hours."
            )
    return issues


def _check_teacher_capacity_vs_load(all_teachers, all_subjects, all_groups,
                                    all_subjectgroups):
    """Check teacher max_hours_week can cover their subjects.

    1. Per teacher: max_hours_week >= max(weekly_hours) of any single subject
    2. Global: total teacher capacity >= total required hours
    """
    subject_ids_in_groups = set()
    for sg in all_subjectgroups:
        subject_ids_in_groups.update(s.id for s in getattr(sg, 'subjects', []))

    issues = []

    for teacher in all_teachers:
        subjects = getattr(teacher, 'subjects', [])
        if not subjects:
            continue
        max_subject_hours = max(s.weekly_hours for s in subjects)
        if teacher.max_hours_week < max_subject_hours:
            subj = next(s for s in subjects if s.weekly_hours == max_subject_hours)
            issues.append(
                f"  - **Teacher \"{teacher.name}\"** has max_hours_week="
                f"{teacher.max_hours_week} but teaches \"{subj.name}\" "
                f"requiring {max_subject_hours}h/week."
            )

    # Global: total teacher capacity vs total required
    total_capacity = sum(t.max_hours_week for t in all_teachers)
    total_required = 0
    for group in all_groups:
        course = group.split("-")[0]
        line_index = _get_line_index(group)
        standalone = sum(
            s.weekly_hours for s in all_subjects
            if s.course_id == course
            and s.id not in subject_ids_in_groups
            and _is_line_included(s, line_index)
        )
        grouped = 0
        for sg in all_subjectgroups:
            if not _is_line_included(sg, line_index):
                continue
            gs = [s for s in getattr(sg, 'subjects', []) if s.course_id == course and _is_line_included(s, line_index)]
            if gs:
                grouped += max(s.weekly_hours for s in gs)
        total_required += standalone + grouped

    if total_required > total_capacity:
        issues.append(
            f"  - **Global capacity**: total required hours ({total_required}h) "
            f"exceed total teacher capacity ({total_capacity}h). "
            f"Need more teachers or reduce subject hours."
        )

    return issues


def _check_teach_every_day_viability(all_subjects, all_groups, num_days):
    """Check subjects with teach_every_day=True are feasible."""
    issues = []
    for subject in all_subjects:
        if not getattr(subject, "teach_every_day", False):
            continue
        sid = subject.id
        # Must have at least num_days total hours
        if subject.weekly_hours < num_days:
            issues.append(
                f"  - **Subject \"{subject.name}\"** has teach_every_day=True "
                f"but only {subject.weekly_hours}h/week (need at least {num_days}h "
                f"for {num_days} days)."
            )
        # Must fit within max_hours_per_day * num_days
        max_possible = subject.max_hours_per_day * num_days
        if subject.weekly_hours > max_possible:
            issues.append(
                f"  - **Subject \"{subject.name}\"** has teach_every_day=True, "
                f"weekly_hours={subject.weekly_hours}, but max possible with "
                f"max_hours_per_day={subject.max_hours_per_day} over {num_days} days "
                f"is {max_possible}h."
            )
    return issues





def _run_sanity_checks(all_teachers, all_subjects, all_groups,
                       all_subjectgroups, num_days, num_hours):
    """Run all pre-solve sanity checks and return a list of issues.

    Combines all Phase 1 checks into one call. Empty list = all clear.
    """
    issues = []
    issues += _check_capacity_sanity(
        all_subjects, all_groups, num_days, num_hours, all_subjectgroups,
    )
    issues += _check_subjects_without_teachers(
        all_subjects, all_teachers, all_groups, all_subjectgroups,
    )
    issues += _check_subjectgroup_weekly_hours_consistency(
        all_subjectgroups,
    )
    issues += _check_teacher_capacity_vs_load(
        all_teachers, all_subjects, all_groups, all_subjectgroups,
    )
    issues += _check_teach_every_day_viability(
        all_subjects, all_groups, num_days,
    )
    logger.info("Sanity checks completed issues=%d", len(issues), extra=build_log_extra())
    return issues


def _run_entity_diagnosis(suspects, all_teachers, all_subjects, all_groups,
                          all_subjectgroups, num_days, num_hours):
    """Phase 3: entity-level diagnosis using assumptions.

    Builds a model with suspect restrictions gated by per-entity assumption
    BoolVars, solves once, and uses SufficientAssumptionsForInfeasibility()
    to identify specific entities involved in the conflict.

    Returns dict mapping restriction_name -> list of entity_info dicts.
    """
    if not suspects:
        return {}, False

    logger.info(
        "Starting entity-level diagnosis suspect_restrictions=%d",
        len(suspects),
        extra=build_log_extra(),
    )

    model = cp_model.CpModel()
    assignments = _create_assignments(
        model, all_teachers, all_subjects, all_groups, num_days, num_hours,
    )

    all_assumptions = []

    for name, restriction, args in _build_hard_restrictions(
        model, assignments, all_teachers, all_subjects,
        all_groups, all_subjectgroups, num_days, num_hours,
    ):
        if name in suspects:
            all_assumptions.extend(restriction.apply_with_assumptions(*args))
        else:
            restriction.apply(*args)

    if not all_assumptions:
        logger.info("Entity-level diagnosis has no assumptions to evaluate", extra=build_log_extra())
        return {}, False

    for assume, _ in all_assumptions:
        model.AddAssumption(assume)

    solver = cp_model.CpSolver()
    timeout_seconds = 300.0
    solver.parameters.max_time_in_seconds = timeout_seconds
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        core_indices = set(solver.SufficientAssumptionsForInfeasibility())

        # SufficientAssumptionsForInfeasibility() returns integer indices,
        # not IntVar objects. Build a mapping from index -> entity_info.
        index_to_info = {assume.Index(): info for assume, info in all_assumptions}

        result = defaultdict(list)
        for idx in core_indices:
            if idx in index_to_info:
                info = index_to_info[idx]
                result[info["restriction"]].append(info)

        logger.info(
            "Entity-level diagnosis found conflicts restrictions=%d core_size=%d",
            len(result),
            len(core_indices),
            extra=build_log_extra(),
        )
        return dict(result), False

    timed_out = status == cp_model.UNKNOWN
    logger.info(
        "Entity-level diagnosis completed status=%s timeout_seconds=%.1f timed_out=%s",
        solver.StatusName(status),
        timeout_seconds,
        timed_out,
        extra=build_log_extra(),
    )
    return {}, timed_out


def diagnose_infeasibility(
    all_teachers, all_subjects, all_groups, all_subjectgroups, num_days, num_hours,
    progress_callback=None,
):
    """Diagnose which restrictions cause infeasibility.

    Phase 1: Capacity sanity checks (instant).
    Phase 2: Isolation testing — re-solve without each restriction
             (10 s timeout per test).
    Phase 3: Entity-level diagnosis using assumptions on suspect
             restrictions (1 solve).

    Args:
        progress_callback: Optional callable(phase: str, partial_markdown: str)
                           called after each phase with accumulated results.

    Returns a dict with keys:
      - sanity_issues: list[str] — Phase 1 issues (empty = all clear)
      - suspects: list[str] — restrictions that cause infeasibility when active
      - cleared: list[str] — restrictions that did NOT cause issues individually
      - entity_conflicts: dict — Phase 3 entity-level results
      - phase3_timed_out: bool — True if Phase 3 timed out without conclusive result
    """
    result: dict[str, list[str] | dict] = {
        "sanity_issues": [],
        "suspects": [],
        "cleared": [],
        "entity_conflicts": {},
        "phase3_timed_out": False,
    }

    # Phase 1: instant capacity and data sanity checks
    logger.info("Diagnosis phase 1 started", extra=build_log_extra())
    sanity_issues = _run_sanity_checks(
        all_teachers, all_subjects, all_groups,
        all_subjectgroups, num_days, num_hours,
    )
    result["sanity_issues"] = sanity_issues
    if result["sanity_issues"]:
        if progress_callback:
            msg = _build_diagnosis_message(result)
            progress_callback("phase1", msg)
        logger.info("Diagnosis ended in phase 1 due to sanity issues=%d", len(sanity_issues), extra=build_log_extra())
        return result

    # Phase 2: isolation testing (hard restrictions only)
    hard_names = [
        "SubjectWeeklyHours",
        "TeacherOneClassAtATime",
        "TeacherUnavailableTimes",
        "TeacherMaxWeeklyHours",
        "GroupSubjectMaxHoursPerDay",
        "GroupAtMostOneLogicalAssignment",
        "GroupSubjectHoursMustBeConsecutive",
        "GroupSubjectHoursMustNotBeConsecutive",
        "LinkedSubjectsConsecutive",
        "SubjectGroupAssignment",
        "SubjectMustEveryDay",
    ]
    logger.info("Diagnosis phase 2 started", extra=build_log_extra())
    for name in hard_names:
        status, _, _ = solve_scheduling_model(
            all_teachers, all_subjects, all_groups, all_subjectgroups,
            num_days, num_hours,
            skip_restrictions={name}, diagnostic_mode=True,
        )
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result["suspects"].append(name)
        else:
            result["cleared"].append(name)

    logger.info(
        "Diagnosis phase 2 completed suspects=%d cleared=%d",
        len(result["suspects"]),
        len(result["cleared"]),
        extra=build_log_extra(),
    )

    if progress_callback:
        msg = _build_diagnosis_message(result)
        progress_callback("phase2", msg)

    # Phase 3: entity-level diagnosis for suspect restrictions
    if result["suspects"]:
        logger.info("Diagnosis phase 3 started", extra=build_log_extra())
        entity_conflicts, phase3_timed_out = _run_entity_diagnosis(
            result["suspects"], all_teachers, all_subjects, all_groups,
            all_subjectgroups, num_days, num_hours,
        )
        result["entity_conflicts"] = entity_conflicts
        result["phase3_timed_out"] = phase3_timed_out
        logger.info(
            "Diagnosis phase 3 completed conflicts=%d timed_out=%s",
            len(entity_conflicts),
            phase3_timed_out,
            extra=build_log_extra(),
        )

    if progress_callback:
        msg = _build_diagnosis_message(result)
        progress_callback("phase3", msg)

    return result


def _build_diagnosis_message(diagnosis):
    """Build markdown diagnosis message from a diagnosis result dict."""
    msg = ["# ❌ No solution found — Diagnostic Results\n"]
    if diagnosis["sanity_issues"]:
        msg.append("## Phase 1 — Capacity sanity checks")
        msg.extend(diagnosis["sanity_issues"])
        msg.append("")
    if diagnosis["suspects"]:
        msg.append("## Phase 2 — Restriction isolation")
        msg.append("Removing any of these restrictions individually makes the model feasible:")
        for name in diagnosis["suspects"]:
            msg.append(f"  - **{name}**")
        msg.append("")
    if diagnosis.get("phase3_timed_out"):
        msg.append("## Phase 3 — Entity diagnosis")
        msg.append("  ⏱️ The diagnosis timed out. The constraints may be too complex")
        msg.append("  for the allocated time. Try increasing timeout or simplifying.")
        msg.append("")
    if diagnosis["entity_conflicts"]:
        msg.append("## Phase 3 — Specific entities involved")
        for restriction_name, entities in diagnosis["entity_conflicts"].items():
            msg.append(f"- **{restriction_name}** — Conflicts involve:")
            for ent in entities:
                name_str = f'{ent["entity_name"]} (id={ent["entity_id"]})'
                extra = ent.get("extra", {})
                if "tutor_group" in extra:
                    name_str += f", tutor of group {extra['tutor_group']}"
                msg.append(f"    - {name_str}")
        msg.append("")
    if diagnosis["cleared"]:
        msg.append("Restrictions that did NOT cause issues individually:")
        for name in diagnosis["cleared"]:
            msg.append(f"  - {name}")
        msg.append("")
    if not diagnosis["sanity_issues"] and not diagnosis["suspects"]:
        msg.append("Could not isolate a single restriction. The infeasibility may arise from")
        msg.append("the interaction of multiple restrictions, or from data configuration.")
    return "\n".join(msg) + "\n"


def create_timetable(session, progress_callback=None, task_id=None) -> str | None:
    """
    Generates the school timetable using the OR-Tools CP-SAT solver.

    This is the main entry point that:
    1. Loads data from the database
    2. Calls solve_scheduling_model to build and solve the model
    3. Saves the results to the database

    Args:
        session: Database session
        progress_callback: Optional callable(phase: str, partial_markdown: str)
                           called after each diagnosis phase completes.
    """

    logger.info("Timetable generation started", extra=build_log_extra(task_id=task_id))

    # --- 1. Data Loading ---
    all_teachers = session.query(Teacher).all()
    all_subjects = session.query(Subject).all()
    all_courses = session.query(Course).all()
    all_subjectgroups = session.query(SubjectGroup).all()
    config = session.query(Config).first()
    logger.info(
        "Loaded scheduling inputs teachers=%d subjects=%d courses=%d subject_groups=%d",
        len(all_teachers),
        len(all_subjects),
        len(all_courses),
        len(all_subjectgroups),
        extra=build_log_extra(task_id=task_id),
    )

    # Create default configuration if none exists
    if not config:
        logger.info("No config found. Creating default configuration", extra=build_log_extra(task_id=task_id))
        config = Config(
            classes_per_day=5, days_per_week=5
        )  # Default: 5 classes per day, 5 days per week
        session.add(config)
        session.commit()
        logger.info(
            "Default configuration created classes_per_day=%d days_per_week=%d",
            config.classes_per_day,
            config.days_per_week,
            extra=build_log_extra(task_id=task_id),
        )

    num_days = config.days_per_week
    num_hours = config.classes_per_day

    # Create a unique list of all class groups (1ºA, 1ºB, 2ºA, etc.)
    all_groups = []
    for course in all_courses:
        for i in range(course.num_lines):
            line_char = chr(ord("A") + i)
            all_groups.append(f"{course.id}-{line_char}")
    logger.info("Computed class groups count=%d", len(all_groups), extra=build_log_extra(task_id=task_id))

    # Parse disabled restrictions from config
    import json as _json
    disabled_raw = getattr(config, 'disabled_restrictions', None)
    skip_restrictions = set(_json.loads(disabled_raw)) if disabled_raw else set()
    logger.info("Loaded disabled restrictions count=%d", len(skip_restrictions), extra=build_log_extra(task_id=task_id))

    # --- 2. Solve the scheduling model ---
    status, assignments, solver = solve_scheduling_model(
        all_teachers, all_subjects, all_groups, all_subjectgroups, num_days, num_hours,
        skip_restrictions=skip_restrictions,
        task_id=task_id,
    )

    # --- 3. Solution Processing ---
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        logger.info("Solver returned feasible solution status=%s", solver.StatusName(status), extra=build_log_extra(task_id=task_id))
        save_solution_to_db(
            session,
            solver,
            assignments,
            all_groups,
            num_days,
            num_hours,
            task_id=task_id,
        )
        session.close()
        logger.info("Timetable generation finished successfully", extra=build_log_extra(task_id=task_id))
        return None
    else:
        logger.warning("No feasible timetable found. Starting diagnosis", extra=build_log_extra(task_id=task_id))
        diagnosis = diagnose_infeasibility(
            all_teachers, all_subjects, all_groups,
            all_subjectgroups, num_days, num_hours,
            progress_callback=progress_callback,
        )
        msg = _build_diagnosis_message(diagnosis)
        logger.warning("Timetable generation finished without solution", extra=build_log_extra(task_id=task_id))
        return msg
