import json
from .models import (
    Course,
    Subject,
    SubjectGroup,
    Teacher,
    Timeslot,
    TimeSlotAssignment,
    Config,
)


def dump_db(session):
    data = {}
    data["courses"] = [c.to_dict() for c in session.query(Course).all()]
    data["subjects"] = [s.to_dict() for s in session.query(Subject).all()]
    data["subject_groups"] = [
        {"id": g.id, "name": g.name, "subjects": [s.id for s in g.subjects]}
        for g in session.query(SubjectGroup).all()
    ]

    teachers = []
    for t in session.query(Teacher).all():
        teachers.append(
            {
                "id": t.id,
                "name": t.name,
                "subjects": [s.id for s in t.subjects],
                "preferences": t.preferences,
                "max_hours_week": t.max_hours_week,
                "tutor_group": t.tutor_group,
            }
        )
    data["teachers"] = teachers

    data["timeslots"] = [
        {
            "id": ts.id,
            "day": ts.day,
            "hour": ts.hour,
            "course_id": ts.course_id,
            "line": ts.line,
            "subject_group_id": ts.subject_group_id,
        }
        for ts in session.query(Timeslot).all()
    ]

    data["assignments"] = [
        {
            "id": a.id,
            "timeslot_id": a.timeslot_id,
            "subject_id": a.subject_id,
            "teacher_id": a.teacher_id,
        }
        for a in session.query(TimeSlotAssignment).all()
    ]

    cfg = session.query(Config).first()
    data["config"] = cfg.to_dict() if cfg else {}
    return data


def import_payload(session, payload):
    """Import a payload (parsed JSON) into the provided session.

    Drops and recreates schema is the caller's responsibility if needed.
    """
    # Config
    cfg_payload = payload.get("config", {}) if isinstance(payload, dict) else {}
    if cfg_payload:
        hour_names = cfg_payload.get("hour_names")
        if hour_names is not None:
            try:
                cfg = Config(
                    classes_per_day=cfg_payload.get("classes_per_day", 5),
                    days_per_week=cfg_payload.get("days_per_week", 5),
                    hour_names=json.dumps(hour_names, ensure_ascii=False),
                    day_indices=json.dumps(
                        cfg_payload.get("day_indices", []), ensure_ascii=False
                    ),
                )
            except Exception:
                cfg = Config(
                    classes_per_day=cfg_payload.get("classes_per_day", 5),
                    days_per_week=cfg_payload.get("days_per_week", 5),
                )
        else:
            cfg = Config(
                classes_per_day=cfg_payload.get("classes_per_day", 5),
                days_per_week=cfg_payload.get("days_per_week", 5),
            )
        session.add(cfg)

    # Courses
    course_map = {}
    for c in payload.get("courses", []) or []:
        course = Course(
            id=c.get("id"), num_lines=c.get("num_lines", c.get("num_lines", 1))
        )
        session.add(course)
        course_map[course.id] = course
    session.flush()

    # Subjects
    subject_map = {}
    for s in payload.get("subjects", []) or []:
        course_id = None
        if "course" in s and isinstance(s["course"], dict):
            course_id = s["course"].get("id")
        elif "course_id" in s:
            course_id = s["course_id"]
        elif "course" in s and isinstance(s["course"], str):
            course_id = s["course"]

        subj = Subject(
            id=s.get("id"),
            name=s.get("name"),
            weekly_hours=s.get("weekly_hours", 1),
            max_hours_per_day=s.get("max_hours_per_day", 2),
            consecutive_hours=s.get("consecutive_hours", True),
            course_id=course_id,
            linked_subject_id=s.get("linked_subject_id", None),
        )
        session.add(subj)
        subject_map[subj.id] = subj
    session.flush()

    # Ensure links are reciprocal
    for subj in list(subject_map.values()):
        linked = getattr(subj, "linked_subject_id", None)
        if linked:
            other = session.get(Subject, linked)
            if other and other.linked_subject_id != subj.id:
                other.linked_subject_id = subj.id
                session.add(other)
    session.flush()

    # Subject groups
    for g in payload.get("subject_groups", []) or []:
        sg = SubjectGroup(name=g.get("name"))
        session.add(sg)
        session.flush()
        members = []
        for sid in g.get("subjects", []) or []:
            s_obj = session.get(Subject, sid)
            if s_obj:
                members.append(s_obj)
        if members:
            sg.subjects = members
    session.flush()

    # Teachers
    for teacher_data in payload.get("teachers", []) or []:
        subj_objs = []
        for sid in teacher_data.get("subjects", []) or []:
            s_obj = session.get(Subject, sid)
            if s_obj:
                subj_objs.append(s_obj)
        teacher = Teacher(
            id=teacher_data.get("id"),
            name=teacher_data.get("name"),
            preferences=teacher_data.get("preferences"),
            max_hours_week=teacher_data.get("max_hours_week", 1),
            tutor_group=teacher_data.get("tutor_group")
            if "tutor_group" in teacher_data
            else None,
        )
        session.add(teacher)
        session.flush()
        if subj_objs:
            teacher.subjects = subj_objs
    session.flush()

    # Timeslots
    ts_map = {}
    for ts in payload.get("timeslots", []) or []:
        timeslot = Timeslot(
            day=ts.get("day"),
            hour=ts.get("hour"),
            course_id=ts.get("course_id"),
            line=ts.get("line"),
            subject_group_id=ts.get("subject_group_id"),
        )
        session.add(timeslot)
        session.flush()
        ts_map[timeslot.id] = timeslot
    session.flush()

    # Assignments
    for a in payload.get("assignments", []) or []:
        timeslot = None
        if a.get("timeslot_id") is not None:
            timeslot = session.get(Timeslot, a.get("timeslot_id"))
        if not timeslot:
            ts_q = session.query(Timeslot)
            if a.get("day"):
                ts_q = ts_q.filter_by(day=a.get("day"))
            if a.get("hour") is not None:
                ts_q = ts_q.filter_by(hour=a.get("hour"))
            if a.get("course_id"):
                ts_q = ts_q.filter_by(course_id=a.get("course_id"))
            if a.get("line") is not None:
                ts_q = ts_q.filter_by(line=a.get("line"))
            timeslot = ts_q.first()

        subject = (
            session.get(Subject, a.get("subject_id"))
            if a.get("subject_id") is not None
            else None
        )
        teacher = (
            session.get(Teacher, a.get("teacher_id"))
            if a.get("teacher_id") is not None
            else None
        )
        if timeslot and subject:
            assign = TimeSlotAssignment(
                timeslot=timeslot,
                subject_id=subject.id,
                teacher_id=(teacher.id if teacher else None),
            )
            session.add(assign)

    session.flush()
