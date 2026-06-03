"""
Module to print markdown timetables for each course line using data from the Activity table.
Each table includes:
- Course/line as a title (e.g., Course: 1ºA)
- Columns for weekdays (Monday to Friday)
- Rows for each hour (Hour 1, Hour 2, etc.)
- Each cell: subject code or name, followed by the teacher's name (e.g., MAT - teacher 1)
"""

from sqlalchemy.orm import Session
from collections import defaultdict
from html import escape
import json
import re
from .models import (
    TimeSlotAssignment,
    Timeslot,
    Config,
    Teacher,
    FixedSlot,
    TeacherBusySlot,
    JointClass,
    SupportAssignment,
    normalize_tutor_groups,
)

from .translations import t
from .markdown_utils import align_tables_in_text


COORDINATION_COLOR = "#e8f5e9"  # light green


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _safe_hex_color(color):
    if isinstance(color, str) and HEX_COLOR_RE.match(color.strip()):
        return color.strip().lower()
    return None


def _build_colored_label_html(label, subject_color):
    safe_label = escape(label)
    safe_color = _safe_hex_color(subject_color)
    if not safe_color:
        return safe_label
    return (
        f"<span class=\"tt-subject-entry\" style=\"background-color: {safe_color};\">"
        f"{safe_label}"
        "</span>"
    )


def _build_colored_label_html_with_data(label, subject_color, data_attrs, extra_classes=""):
    safe_label = escape(label)
    safe_color = _safe_hex_color(subject_color)
    attrs = " ".join(f'data-{k}="{escape(str(v))}"' for k, v in data_attrs.items())
    base_class = "tt-support-entry"
    if extra_classes:
        base_class += f" {extra_classes}"
    if not safe_color:
        return f"<span class=\"{base_class}\" {attrs}>{safe_label}</span>"
    return (
        f"<span class=\"{base_class} tt-subject-entry\" "
        f"style=\"background-color: {safe_color};\" {attrs}>"
        f"{safe_label}"
        "</span>"
    )


def _build_fixed_slot_html(label):
    safe_label = escape(label)
    return (
        f"<span class=\"tt-fixed-slot\">{safe_label}</span>"
    )


def _build_colored_assignment_html(subject_name, teacher_name, subject_color):
    label = f"{subject_name} ({teacher_name})"
    return _build_colored_label_html(label, subject_color)


def get_timetables_from_db(session):
    """
    Retrieves timetable data from the Activity table and organizes it per course line.
    Handles multiple subjects in the same timeslot (SubjectGroups).
    Returns:
        Dict[str, Dict[(int, int), List[str]]]:
            {course_line: {(hour, day_index): [subject_teacher_strings]}}
    """
    timetable = defaultdict(lambda: defaultdict(list))
    assignments = session.query(TimeSlotAssignment).all()
    for assignment in assignments:
        timeslot: Timeslot = assignment.timeslot
        course_line = (
            f"{timeslot.course_id}{chr(ord('A') + timeslot.line)}"  # e.g., "1ºA"
        )
        hour = timeslot.hour  # e.g., 1, 2, ...
        # weekday stored as an index (0 = first weekday)
        weekday = timeslot.day
        subject_name = assignment.subject.name
        teacher_name = assignment.teacher.name
        group_color = None
        if timeslot.subject_group is not None:
            group_color = getattr(timeslot.subject_group, "color", None)
        subject_color = group_color or assignment.subject.color
        timetable[course_line][(hour, weekday)].append(
            _build_colored_assignment_html(subject_name, teacher_name, subject_color)
        )

    # Append support assignments to course timetable cells
    support_assignments = session.query(SupportAssignment).all()
    for sa in support_assignments:
        course_line = f"{sa.course_id}{chr(ord('A') + sa.line)}"
        support_label = f"{sa.teacher.name} ({t('timetable.support_label')})"
        timetable[course_line][(sa.hour, sa.day)].append(
            _build_colored_label_html(support_label, sa.subject.color)
        )

    return timetable


def _interleave_rows(sorted_hours, fixed_slots_sorted):
    """Interleave solver rows with fixed slot rows by position.

    Args:
        sorted_hours: List of hour indices from solver output.
        fixed_slots_sorted: List of FixedSlot sorted by position.

    Yields:
        Tuple of (row_type: str, data) where:
        - ("solver", hour_index)
        - ("fixed", fixed_slot)
    """
    solver_idx = 0
    fixed_idx = 0
    position = 1

    while solver_idx < len(sorted_hours) or fixed_idx < len(fixed_slots_sorted):
        next_fixed = fixed_slots_sorted[fixed_idx] if fixed_idx < len(fixed_slots_sorted) else None
        next_fixed_pos = next_fixed.position if next_fixed else None

        if next_fixed_pos is not None and next_fixed_pos == position:
            yield ("fixed", next_fixed)
            fixed_idx += 1
        elif solver_idx < len(sorted_hours):
            yield ("solver", sorted_hours[solver_idx])
            solver_idx += 1
        position += 1


def generate_markdown_timetable_by_course(
    timetable,
    tutors_dict,
    cfg_dict=None,
    course_fixed_slots=None,
):
    """
    Generates markdown tables for each course line without requiring database session.

    Args:
        timetable: Dict[str, Dict[(int, int), List[str]]]
                  {course_line: {(hour, day_index): [subject_teacher_strings]}}
        tutors_dict: Dict[str, str] mapping course_line to tutor_name
                    (e.g., {"1-A": "John", "1-B": "Jane"})
        cfg_dict: Optional dict with configuration:
                 - hour_names: List of hour labels
                 - day_indices: List of day indices
                 - days_per_week: Number of days per week
        course_fixed_slots: Optional list of FixedSlot objects for courses.

    Returns:
        str: The generated markdown string.
    """
    all_hours = set()
    for course in timetable.values():
        all_hours.update(hour for (hour, _) in course.keys())
    sorted_hours = sorted(all_hours)

    cfg_hour_names = cfg_dict.get("hour_names", []) if cfg_dict else []
    days_per_week = cfg_dict.get("days_per_week", 5) if cfg_dict else 5
    # day_indices may be present but None; ensure it's iterable
    day_indices_from_cfg = None
    if cfg_dict is not None:
        day_indices_from_cfg = cfg_dict.get("day_indices")

    if course_fixed_slots is None:
        course_fixed_slots = []
    fixed_slots_sorted = sorted(course_fixed_slots, key=lambda fs: fs.position)

    markdown = []
    markdown.append("## " + t("timetable.by_course") + "\n")
    for course_line in sorted(timetable.keys()):
        slots = timetable[course_line]
        course_label = t("timetable.course_label")
        tutor_label = t("timetable.group_tutor")

        # Get tutor from the provided dict
        tutor_name = tutors_dict.get(course_line)
        if tutor_name:
            markdown.append(
                f"### {course_label}: {course_line} — {tutor_label}: {tutor_name}"
            )
        else:
            markdown.append(f"### {course_label}: {course_line}")

        day_indices = (
            day_indices_from_cfg
            if day_indices_from_cfg is not None
            else list(range(days_per_week))
        )
        weekdays = [t(f"day.{i}") for i in day_indices]
        header = "| " + t("timetable.hour_header") + " | " + " | ".join(weekdays) + " |"
        separator = "|-------" + "|".join(["-------"] * (len(weekdays) + 1)) + "|"
        markdown.append(header)
        markdown.append(separator)

        fixed_slots_for_course = [
            fs for fs in fixed_slots_sorted
        ]
        for row_type, data in _interleave_rows(sorted_hours, fixed_slots_for_course):
            if row_type == "fixed":
                fs = data
                row = [_build_fixed_slot_html(fs.label) for _ in range(len(weekdays))]
                hour_label = fs.time_range
            else:
                hour = data
                row = []
                for day_index in range(len(weekdays)):
                    assignments = slots.get((hour, day_index), [])
                    if assignments:
                        cell = " <br>".join(assignments)
                    else:
                        cell = ""
                    row.append(cell)
                hour_label = (
                    cfg_hour_names[hour]
                    if hour < len(cfg_hour_names)
                    else t("hours.label").format(n=hour + 1)
                )
            markdown.append(f"| {hour_label} | " + " | ".join(row) + " |")
        markdown.append("")
    result = "\n".join(markdown)
    # Align markdown tables for nicer plaintext rendering
    result = align_tables_in_text(result)
    return result


def print_markdown_timetable_from_assignments(session) -> str:
    """
    Prints and returns markdown tables for each course line using Activity table data.
    Handles multiple subjects per timeslot (SubjectGroups).
    Args:
        session: Database session
    Returns:
        str: The generated markdown string.
    """
    timetable = get_timetables_from_db(session)

    # Build tutors_dict from database
    tutors_dict = {}
    teachers = session.query(Teacher).all()
    for teacher in teachers:
        for tutor_group in normalize_tutor_groups(teacher.tutor_group):
            tutors_dict[tutor_group] = teacher.name

    cfg = session.query(Config).first()
    cfg_dict = cfg.to_dict() if cfg else None

    course_fixed_slots = session.query(FixedSlot).filter_by(slot_type="course").all()

    return generate_markdown_timetable_by_course(
        timetable, tutors_dict, cfg_dict,
        course_fixed_slots=course_fixed_slots,
    )


def get_teacher_timetables_from_db(session):
    """
    Retrieve timetables from the database and organize them by teacher.
    Includes both teaching assignments (TimeSlotAssignment) and non-teaching
    busy slots (TeacherBusySlot) such as coordination hours.
    Returns:
        Dict[teacher_name, Dict[(hour, day_index), List[str]]]
    """
    teacher_timetable = defaultdict(lambda: defaultdict(list))

    # Build JointClass lookup: (course_id, subject_id, line_letter) -> [JointClass]
    joint_classes = session.query(JointClass).all()
    jc_lookup = {}
    for jc in joint_classes:
        lines = json.loads(jc.lines) if isinstance(jc.lines, str) else jc.lines
        for line_letter in lines:
            key = (jc.course_id, jc.subject_id, line_letter)
            jc_lookup.setdefault(key, []).append(jc)

    # First pass: collect raw items per (teacher, hour, day) cell
    cell_items = defaultdict(list)
    assignments = session.query(TimeSlotAssignment).all()
    for assignment in assignments:
        timeslot = assignment.timeslot
        teacher_name = assignment.teacher.name
        subject_name = assignment.subject.name
        course_line = f"{timeslot.course_id}{chr(ord('A') + timeslot.line)}"

        line_letter = chr(ord('A') + timeslot.line)
        matched_jc = None
        for jc in jc_lookup.get((timeslot.course_id, assignment.subject_id, line_letter), []):
            if jc.teacher_id is None or jc.teacher_id == assignment.teacher_id:
                matched_jc = jc
                break

        group_color = None
        if timeslot.subject_group is not None:
            group_color = getattr(timeslot.subject_group, "color", None)
        subject_color = group_color or assignment.subject.color

        cell_items[(teacher_name, timeslot.hour, timeslot.day)].append({
            "jc": matched_jc,
            "subject_name": subject_name,
            "course_line": course_line,
            "subject_color": subject_color,
        })

    # Second pass: build labels, merging entries of the same JointClass
    for (teacher_name, hour, day), items in cell_items.items():
        jc_groups = defaultdict(list)
        for item in items:
            key = id(item["jc"]) if item["jc"] else None
            jc_groups[key].append(item)

        for group_key, group in jc_groups.items():
            if group_key is not None and len(group) > 1:
                jc = group[0]["jc"]
                if jc.name:
                    display_name = jc.name
                else:
                    display_name = f"{group[0]['subject_name']} ({t('timetable.joint_class_label')})"
                teacher_timetable[teacher_name][(hour, day)].append(
                    _build_colored_label_html(display_name, group[0]["subject_color"])
                )
            else:
                for item in group:
                    display_name = item["subject_name"]
                    if item["jc"]:
                        jc = item["jc"]
                        display_name = jc.name or f"{item['subject_name']} ({t('timetable.joint_class_label')})"
                    teacher_timetable[teacher_name][(hour, day)].append(
                        _build_colored_label_html(f"{item['course_line']}: {display_name}", item["subject_color"])
                    )

    # Build teacher preferences lookup for unavailable slots
    all_teachers = session.query(Teacher).all()
    teacher_unavailable = {}
    for teacher in all_teachers:
        prefs = {}
        if teacher.preferences:
            try:
                prefs = json.loads(teacher.preferences)
            except (ValueError, TypeError):
                prefs = {}
        unavailable_set = set()
        for day_str, day_prefs in prefs.items():
            if isinstance(day_prefs, dict) and "unavailable" in day_prefs:
                for h in day_prefs["unavailable"]:
                    unavailable_set.add((int(day_str), h))
        teacher_unavailable[teacher.name] = unavailable_set

    # Support assignments
    support_assignments = session.query(SupportAssignment).all()
    for sa in support_assignments:
        teacher_name = sa.teacher.name
        course_line = f"{sa.course_id}{chr(ord('A') + sa.line)}"
        label = f"{course_line}: {sa.subject.name} ({t('timetable.support_label')})"
        data = {
            "support-id": sa.id,
            "teacher": sa.teacher.name,
            "day": sa.day,
            "hour": sa.hour,
        }
        unavailable = teacher_unavailable.get(teacher_name, set())
        if (sa.day, sa.hour) in unavailable:
            data["conflict"] = "1"
            safe_label = escape(label)
            safe_color = _safe_hex_color(sa.subject.color)
            base_class = "tt-support-entry tt-support-conflict tt-subject-entry"
            attrs = " ".join(f'data-{k}="{escape(str(v))}"' for k, v in data.items())
            if safe_color:
                html = (
                    f'<span class="{base_class}" style="background-color: {safe_color};" {attrs}>'
                    f'{safe_label}'
                    f'<span class="tt-conflict-warning">⚠️</span>'
                    f'</span>'
                )
            else:
                html = (
                    f'<span class="{base_class}" {attrs}>'
                    f'{safe_label}'
                    f'<span class="tt-conflict-warning">⚠️</span>'
                    f'</span>'
                )
            teacher_timetable[teacher_name][(sa.hour, sa.day)].append(html)
        else:
            teacher_timetable[teacher_name][(sa.hour, sa.day)].append(
                _build_colored_label_html_with_data(label, sa.subject.color, data)
            )

    # Non-teaching busy slots (coordination, etc.)
    busy_slots = session.query(TeacherBusySlot).all()
    for slot in busy_slots:
        coord_label = _build_colored_label_html(
            t("timetable.coordination_label"), COORDINATION_COLOR
        )
        teacher_timetable[slot.teacher.name][(slot.hour, slot.day)].append(coord_label)

    # Fill remaining gaps
    cfg = session.query(Config).first()
    num_days = cfg.days_per_week if cfg else 5
    num_hours = cfg.classes_per_day if cfg else 5

    for teacher_name, slots in list(teacher_timetable.items()):
        unavailable = teacher_unavailable.get(teacher_name, set())
        for d in range(num_days):
            for h in range(num_hours):
                key = (h, d)
                if key not in slots:
                    if (d, h) in unavailable:
                        slots[key].append(
                            f'<span class="tt-unavailable" data-teacher="{escape(teacher_name)}" data-day="{d}" data-hour="{h}">✕</span>'
                        )
                    else:
                        slots[key].append(
                            f'<span class="tt-gap" data-teacher="{escape(teacher_name)}" data-day="{d}" data-hour="{h}"></span>'
                        )

    return teacher_timetable


def generate_markdown_timetable_by_teacher(
    teacher_timetable,
    teachers_info,
    teachers_tutors=None,
    teachers_assigned=None,
    teachers_coordination=None,
    teachers_support=None,
    cfg_dict=None,
    teacher_fixed_slots=None,
):
    """
    Generates markdown tables of the timetable for each teacher without requiring database session.

    Args:
        teacher_timetable: Dict[teacher_name, Dict[(int, int), List[str]]]
                          {teacher_name: {(hour, day_index): [course_subject_strings]}}
        teachers_info: Dict[teacher_name, max_hours_week]
        cfg_dict: Optional dict with configuration:
                 - hour_names: List of hour labels
                 - day_indices: List of day indices
                 - days_per_week: Number of days per week
        teacher_fixed_slots: Optional list of FixedSlot objects for teachers.

    Returns:
        str: The generated markdown string.
    """
    all_hours = set()
    for teacher in teacher_timetable.values():
        all_hours.update(hour for (hour, _) in teacher.keys())
    sorted_hours = sorted(all_hours)

    cfg_hour_names = cfg_dict.get("hour_names", []) if cfg_dict else []
    days_per_week = cfg_dict.get("days_per_week", 5) if cfg_dict else 5
    day_indices_from_cfg = None
    if cfg_dict is not None:
        day_indices_from_cfg = cfg_dict.get("day_indices")

    if teacher_fixed_slots is None:
        teacher_fixed_slots = []
    fixed_slots_sorted = sorted(teacher_fixed_slots, key=lambda fs: fs.position)

    markdown = []
    markdown.append("## " + t("timetable.by_teacher") + "\n")
    for teacher_name in sorted(teacher_timetable.keys()):
        slots = teacher_timetable[teacher_name]
        max_hours = teachers_info.get(teacher_name, 0)
        assigned_hours = (teachers_assigned or {}).get(teacher_name, 0)
        coord_hours = (teachers_coordination or {}).get(teacher_name, 0)
        support_hours = (teachers_support or {}).get(teacher_name, 0)
        lective_hours = assigned_hours
        total_occupied = lective_hours + coord_hours + support_hours
        parts = []
        if lective_hours > 0:
            parts.append(f"{lective_hours}h {t('timetable.lective_label')}")
        if coord_hours > 0:
            parts.append(f"{coord_hours}h {t('timetable.coordination_label_short')}")
        if support_hours > 0:
            parts.append(f"{support_hours}h {t('timetable.support_label_short')}")
        if not parts:
            parts.append(f"{total_occupied}h")
        total_str = f"{total_occupied}h/{max_hours}h"
        if max_hours > 0 and total_occupied != max_hours:
            total_str = f'<span style="color:red">{total_occupied}h/{max_hours}h</span>'
        hours_info = f"({total_str}): ({', '.join(parts)})"
        # If a mapping of teacher -> tutor_group is provided, show it after the name
        tutor_suffix = ""
        if teachers_tutors:
            tutor_group = teachers_tutors.get(teacher_name)
            if tutor_group:
                tutor_suffix = f" — {t('timetable.group_tutor')}: {tutor_group}"
        markdown.append(f"### {teacher_name}{tutor_suffix}")
        markdown.append(f"{hours_info}")
        # Markdown table header
        day_indices = (
            day_indices_from_cfg
            if day_indices_from_cfg is not None
            else list(range(days_per_week))
        )
        weekdays = [t(f"day.{i}") for i in day_indices]
        header = "| " + t("timetable.hour_header") + " | " + " | ".join(weekdays) + " |"
        separator = "|-------" + "|".join(["-------"] * (len(weekdays) + 1)) + "|"
        markdown.append(header)
        markdown.append(separator)

        fixed_slots_for_teacher = [
            fs for fs in fixed_slots_sorted
        ]
        for row_type, data in _interleave_rows(sorted_hours, fixed_slots_for_teacher):
            if row_type == "fixed":
                fs = data
                row = [_build_fixed_slot_html(fs.label) for _ in range(len(weekdays))]
                hour_label = fs.time_range
            else:
                hour = data
                row = []
                for day_index in range(len(weekdays)):
                    assignments = slots.get((hour, day_index), [])
                    if assignments:
                        cell = " <br> ".join(assignments)
                    else:
                        cell = ""
                    row.append(cell)
                hour_label = (
                    cfg_hour_names[hour]
                    if hour < len(cfg_hour_names)
                    else t("hours.label").format(n=hour + 1)
                )
            markdown.append(f"| {hour_label} | " + " | ".join(row) + " |")
        markdown.append("")
    result = "\n".join(markdown)
    # Align markdown tables for nicer plaintext rendering
    result = align_tables_in_text(result)
    return result


def print_markdown_timetable_per_teacher(session) -> str:
    """
    Returns markdown tables of the timetable for each teacher using Activity data.
    Each cell contains the course (e.g., 1ºA) and the subject.
    Handles multiple subjects per timeslot (SubjectGroups).
    The tables are ordered by teacher name.
    Args:
        session: Database session
    """
    teacher_timetable = get_teacher_timetables_from_db(session)

    from .teacher_utils import compute_teacher_hours
    hours_data = compute_teacher_hours(session)

    teachers_info = {}
    teachers_assigned = {}
    teachers_coordination = {}
    teachers_support = {}
    for tid, data in hours_data.items():
        teachers_info[data['name']] = data['max_hours_week']
        teachers_assigned[data['name']] = data['assigned_hours']
        teachers_coordination[data['name']] = data['coordination_hours']
        teachers_support[data['name']] = data['support_hours']

    # Build a mapping of teacher name -> tutor_group (if any)
    teachers_tutors = {}
    teachers = session.query(Teacher).all()
    for teacher in teachers:
        tutor_groups = normalize_tutor_groups(teacher.tutor_group)
        if tutor_groups:
            teachers_tutors[teacher.name] = ", ".join(tutor_groups)

    cfg = session.query(Config).first()
    cfg_dict = cfg.to_dict() if cfg else None

    teacher_fixed_slots = session.query(FixedSlot).filter_by(slot_type="teacher").all()

    return generate_markdown_timetable_by_teacher(
        teacher_timetable, teachers_info, teachers_tutors,
        teachers_assigned=teachers_assigned,
        teachers_coordination=teachers_coordination,
        teachers_support=teachers_support,
        cfg_dict=cfg_dict,
        teacher_fixed_slots=teacher_fixed_slots,
    )


# Example usage:
if __name__ == "__main__":
    session = Session()
    print_markdown_timetable_from_assignments(session)
    print_markdown_timetable_per_teacher(session)
