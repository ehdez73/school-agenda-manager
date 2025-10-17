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
from .models import TimeSlotAssignment, Timeslot, Config, Teacher

from .translations import t
from .markdown_utils import align_tables_in_text


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
        timetable[course_line][(hour, weekday)].append(
            f"{subject_name} ({teacher_name})"
        )
    return timetable


def generate_markdown_timetable_by_course(
    timetable,
    tutors_dict,
    cfg_dict=None,
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
        for hour in sorted_hours:
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
        if teacher.tutor_group:
            tutors_dict[teacher.tutor_group] = teacher.name

    cfg = session.query(Config).first()
    cfg_dict = cfg.to_dict() if cfg else None

    return generate_markdown_timetable_by_course(timetable, tutors_dict, cfg_dict)


def get_teacher_timetables_from_db(session):
    """
    Retrieve timetables from the Activity table and organize them by teacher.
    Handles multiple subjects in the same timeslot (SubjectGroups).
    Returns:
        Dict[teacher_name, Dict[(hour, day_index), List[str]]]
    """
    teacher_timetable = defaultdict(lambda: defaultdict(list))
    assignments = session.query(TimeSlotAssignment).all()
    for assignment in assignments:
        timeslot = assignment.timeslot
        teacher_name = assignment.teacher.name
        hour = timeslot.hour
        weekday = timeslot.day
        subject_name = assignment.subject.name
        course_line = f"{timeslot.course_id}{chr(ord('A') + timeslot.line)}"
        teacher_timetable[teacher_name][(hour, weekday)].append(
            f"{course_line}: {subject_name}"
        )
    return teacher_timetable


def generate_markdown_timetable_by_teacher(
    teacher_timetable,
    teachers_info,
    teachers_tutors=None,
    cfg_dict=None,
):
    """
    Generates markdown tables of the timetable for each teacher without requiring database session.

    Args:
        teacher_timetable: Dict[teacher_name, Dict[(hour, day_index), List[str]]]
                          {teacher_name: {(hour, day_index): [course_subject_strings]}}
        teachers_info: Dict[teacher_name, max_hours_week]
        cfg_dict: Optional dict with configuration:
                 - hour_names: List of hour labels
                 - day_indices: List of day indices
                 - days_per_week: Number of days per week

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

    # Calculate assigned hours for each teacher
    teacher_assigned_hours = {}
    for teacher_name, slots in teacher_timetable.items():
        total_hours = sum(len(assignments) for assignments in slots.values())
        teacher_assigned_hours[teacher_name] = total_hours

    markdown = []
    markdown.append("## " + t("timetable.by_teacher") + "\n")
    for teacher_name in sorted(teacher_timetable.keys()):
        slots = teacher_timetable[teacher_name]
        assigned_hours = teacher_assigned_hours[teacher_name]
        max_hours = teachers_info.get(teacher_name, 0)
        hours_info = t(
            "timetable.teacher_hours", assigned=assigned_hours, max=max_hours
        )
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
        for hour in sorted_hours:
            row = []
            for day_index in range(len(weekdays)):
                assignments = slots.get((hour, day_index), [])
                if assignments:
                    # Join multiple assignments with markdown line breaks (double space + newline)
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

    # Get teacher information for hours calculation
    teachers_info = {}
    teachers = session.query(Teacher).all()
    for teacher in teachers:
        teachers_info[teacher.name] = teacher.max_hours_week

    # Build a mapping of teacher name -> tutor_group (if any)
    teachers_tutors = {}
    for teacher in teachers:
        if teacher.tutor_group:
            teachers_tutors[teacher.name] = teacher.tutor_group

    cfg = session.query(Config).first()
    cfg_dict = cfg.to_dict() if cfg else None

    return generate_markdown_timetable_by_teacher(
        teacher_timetable, teachers_info, teachers_tutors, cfg_dict
    )


# Example usage:
if __name__ == "__main__":
    session = Session()
    print_markdown_timetable_from_assignments(session)
    print_markdown_timetable_per_teacher(session)
