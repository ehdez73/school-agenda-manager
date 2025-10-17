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
    all_hours = set()
    for course in timetable.values():
        all_hours.update(hour for (hour, _) in course.keys())
    sorted_hours = sorted(all_hours)

    cfg = session.query(Config).first()
    cfg_dict = cfg.to_dict() if cfg else None
    cfg_hour_names = cfg_dict.get("hour_names", []) if cfg_dict else []

    markdown = []
    markdown.append("## " + t("timetable.by_course") + "\n")
    for course_line in sorted(timetable.keys()):
        slots = timetable[course_line]
        course_label = t("timetable.course_label")
        markdown.append(f"### {course_label}: {course_line}")
        day_indices = (
            cfg_dict.get("day_indices")
            if cfg_dict
            else list(range(cfg.days_per_week if cfg else 5))
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
    return result


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
    all_hours = set()
    for teacher in teacher_timetable.values():
        all_hours.update(hour for (hour, _) in teacher.keys())
    sorted_hours = sorted(all_hours)

    cfg = session.query(Config).first()
    cfg_dict = cfg.to_dict() if cfg else None
    cfg_hour_names = cfg_dict.get("hour_names", []) if cfg_dict else []

    # Get teacher information for hours calculation
    teachers_info = {}
    teachers = session.query(Teacher).all()
    for teacher in teachers:
        teachers_info[teacher.name] = teacher.max_hours_week

    # Calculate assigned hours for each teacher
    teacher_assigned_hours = defaultdict(int)
    assignments = session.query(TimeSlotAssignment).all()
    for assignment in assignments:
        teacher_name = assignment.teacher.name
        teacher_assigned_hours[teacher_name] += 1

    markdown = []
    markdown.append("## " + t("timetable.by_teacher") + "\n")
    for teacher_name in sorted(teacher_timetable.keys()):
        slots = teacher_timetable[teacher_name]
        assigned_hours = teacher_assigned_hours[teacher_name]
        max_hours = teachers_info.get(teacher_name, 0)
        hours_info = t(
            "timetable.teacher_hours", assigned=assigned_hours, max=max_hours
        )
        markdown.append(f"### {teacher_name}")
        markdown.append(f"{hours_info}")
        # Markdown table header
        day_indices = (
            cfg_dict.get("day_indices")
            if cfg_dict
            else list(range(cfg.days_per_week if cfg else 5))
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
    return result


# Example usage:
if __name__ == "__main__":
    session = Session()
    print_markdown_timetable_from_assignments(session)
    print_markdown_timetable_per_teacher(session)
