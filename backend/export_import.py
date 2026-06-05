import json as _json
from sqlalchemy import delete
from .models import (
    Course,
    Subject,
    SubjectGroup,
    Teacher,
    Timeslot,
    TimeSlotAssignment,
    Config,
    FixedSlot,
    TeacherBusySlot,
    JointClass,
    SupportAssignment,
    TeacherFixedSlotLabel,
    CourseFixedSlotLabel,
    normalize_tutor_groups,
    teacher_subject,
)


def dump_db(session):
    data = {}
    data["courses"] = [c.to_dict() for c in session.query(Course).all()]
    data["subjects"] = [s.to_dict() for s in session.query(Subject).all()]
    data["subject_groups"] = [
        {
            "id": g.id,
            "name": g.name,
            "color": g.color,
            "subjects": [s.id for s in g.subjects],
            "included_lines": _json.loads(g.included_lines) if g.included_lines else None,
            "shared_hours": g.shared_hours,
        }
        for g in session.query(SubjectGroup).all()
    ]

    teachers = []
    for t in session.query(Teacher).all():
        ts_rows = session.execute(
            teacher_subject.select().where(teacher_subject.c.teacher_id == t.id)
        ).fetchall()
        teacher_subject_lines = {}
        for _, subject_id, included_lines in ts_rows:
            if included_lines is not None:
                try:
                    teacher_subject_lines[str(subject_id)] = _json.loads(included_lines)
                except (ValueError, TypeError):
                    teacher_subject_lines[str(subject_id)] = None
            else:
                teacher_subject_lines[str(subject_id)] = None
        teachers.append(
            {
                "id": t.id,
                "name": t.name,
                "subjects": [s.id for s in t.subjects],
                "teacher_subject_lines": teacher_subject_lines,
                "preferences": t.preferences,
                "coordination_hours": t.coordination_hours,
                "max_hours_week": t.max_hours_week,
                "tutor_group": t.tutor_group,
                "tutor_groups": normalize_tutor_groups(t.tutor_group),
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

    data["fixed_slots"] = [fs.to_dict() for fs in session.query(FixedSlot).all()]

    data["teacher_fixed_slot_labels"] = [
        {
            "id": lbl.id,
            "teacher_id": lbl.teacher_id,
            "fixed_slot_id": lbl.fixed_slot_id,
            "day": lbl.day,
            "label": lbl.label,
        }
        for lbl in session.query(TeacherFixedSlotLabel).all()
    ]

    data["course_fixed_slot_labels"] = [
        {
            "id": lbl.id,
            "course_line": lbl.course_line,
            "fixed_slot_id": lbl.fixed_slot_id,
            "day": lbl.day,
            "label": lbl.label,
        }
        for lbl in session.query(CourseFixedSlotLabel).all()
    ]

    data["teacher_busy_slots"] = [
        {
            "id": bs.id,
            "teacher_id": bs.teacher_id,
            "day": bs.day,
            "hour": bs.hour,
            "slot_type": bs.slot_type,
        }
        for bs in session.query(TeacherBusySlot).all()
    ]

    data["joint_classes"] = [
        {
            "id": jc.id,
            "name": jc.name,
            "course_id": jc.course_id,
            "subject_id": jc.subject_id,
            "teacher_id": jc.teacher_id,
            "lines": _json.loads(jc.lines) if jc.lines else [],
            "shared_hours": jc.shared_hours,
        }
        for jc in session.query(JointClass).all()
    ]

    data["support_assignments"] = [
        {
            "id": sa.id,
            "teacher_id": sa.teacher_id,
            "day": sa.day,
            "hour": sa.hour,
            "subject_id": sa.subject_id,
            "course_id": sa.course_id,
            "line": sa.line,
        }
        for sa in session.query(SupportAssignment).all()
    ]

    return data


def import_payload(session, payload):
    """Import a payload (parsed JSON) into the provided session.

    Drops and recreates schema is the caller's responsibility if needed.
    """
    # Config
    cfg_payload = payload.get("config", {}) if isinstance(payload, dict) else {}
    if cfg_payload:
        hour_names = cfg_payload.get("hour_names")
        disabled_raw = cfg_payload.get("disabled_restrictions")
        try:
            disabled_restrictions = _json.dumps(disabled_raw, ensure_ascii=False) if disabled_raw is not None else None
        except Exception:
            disabled_restrictions = None

        if hour_names is not None:
            try:
                cfg = Config(
                    classes_per_day=cfg_payload.get("classes_per_day", 5),
                    days_per_week=cfg_payload.get("days_per_week", 5),
                    hour_names=_json.dumps(hour_names, ensure_ascii=False),
                    day_indices=_json.dumps(
                        cfg_payload.get("day_indices", []), ensure_ascii=False
                    ),
                    disabled_restrictions=disabled_restrictions,
                )
            except Exception:
                cfg = Config(
                    classes_per_day=cfg_payload.get("classes_per_day", 5),
                    days_per_week=cfg_payload.get("days_per_week", 5),
                    disabled_restrictions=disabled_restrictions,
                )
        else:
            cfg = Config(
                classes_per_day=cfg_payload.get("classes_per_day", 5),
                days_per_week=cfg_payload.get("days_per_week", 5),
                disabled_restrictions=disabled_restrictions,
            )
        session.add(cfg)

    # Fixed slots
    for fs in payload.get("fixed_slots", []) or []:
        fixed = FixedSlot(
            slot_type=fs.get("slot_type"),
            position=fs.get("position"),
            label=fs.get("label"),
            time_range=fs.get("time_range"),
            color=fs.get("color", "#f1f5f9"),
        )
        session.add(fixed)
    session.flush()

    # Teacher fixed slot labels
    for lbl in payload.get("teacher_fixed_slot_labels", []) or []:
        label = TeacherFixedSlotLabel(
            teacher_id=lbl.get("teacher_id"),
            fixed_slot_id=lbl.get("fixed_slot_id"),
            day=lbl.get("day"),
            label=lbl.get("label", ""),
        )
        session.add(label)
    session.flush()

    # Course fixed slot labels
    for lbl in payload.get("course_fixed_slot_labels", []) or []:
        label = CourseFixedSlotLabel(
            course_line=lbl.get("course_line"),
            fixed_slot_id=lbl.get("fixed_slot_id"),
            day=lbl.get("day"),
            label=lbl.get("label", ""),
        )
        session.add(label)
    session.flush()

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

        incl_lines = s.get("included_lines", None)
        if incl_lines is not None:
            incl_lines = _json.dumps(incl_lines)

        subj = Subject(
            id=s.get("id"),
            name=s.get("name"),
            color=s.get("color", "#dbeafe"),
            weekly_hours=s.get("weekly_hours", 1),
            max_hours_per_day=s.get("max_hours_per_day", 2),
            consecutive_hours=s.get("consecutive_hours", True),
            teach_every_day=s.get("teach_every_day", False),
            course_id=course_id,
            linked_subject_id=s.get("linked_subject_id", None),
            included_lines=incl_lines,
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
        incl_lines = g.get("included_lines", None)
        if incl_lines is not None:
            incl_lines = _json.dumps(incl_lines)

        sg = SubjectGroup(
            name=g.get("name"),
            color=g.get("color", "#fef3c7"),
            included_lines=incl_lines,
            shared_hours=g.get("shared_hours"),
        )
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
        teacher = Teacher(
            id=teacher_data.get("id"),
            name=teacher_data.get("name"),
            preferences=teacher_data.get("preferences"),
            coordination_hours=teacher_data.get("coordination_hours", 0),
            max_hours_week=teacher_data.get("max_hours_week", 1),
        )
        teacher.set_tutor_groups(teacher_data.get("tutor_groups", teacher_data.get("tutor_group")))
        session.add(teacher)
        session.flush()
        ts_lines = teacher_data.get("teacher_subject_lines") or {}
        if ts_lines or teacher_data.get("subjects"):
            session.execute(
                delete(teacher_subject).where(teacher_subject.c.teacher_id == teacher.id)
            )
            for subject_id in teacher_data.get("subjects", []) or []:
                included = ts_lines.get(str(subject_id))
                included_json = _json.dumps(included) if included is not None else None
                session.execute(
                    teacher_subject.insert().values(
                        teacher_id=teacher.id,
                        subject_id=subject_id,
                        included_lines=included_json,
                    )
                )
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

    # Teacher busy slots (coordination, etc.)
    for bs in payload.get("teacher_busy_slots", []) or []:
        teacher = session.get(Teacher, bs.get("teacher_id"))
        if teacher:
            busy_slot = TeacherBusySlot(
                teacher_id=teacher.id,
                day=bs.get("day", 0),
                hour=bs.get("hour", 0),
                slot_type=bs.get("slot_type", "coordinacion"),
            )
            session.add(busy_slot)

    # Joint classes
    for jc in payload.get("joint_classes", []) or []:
        lines = jc.get("lines", [])
        joint = JointClass(
            name=jc.get("name"),
            course_id=jc.get("course_id"),
            subject_id=jc.get("subject_id"),
            teacher_id=jc.get("teacher_id"),
            lines=_json.dumps(lines) if isinstance(lines, list) else lines,
            shared_hours=jc.get("shared_hours"),
        )
        session.add(joint)

    # Support assignments
    for sa in payload.get("support_assignments", []) or []:
        support = SupportAssignment(
            teacher_id=sa.get("teacher_id"),
            day=sa.get("day"),
            hour=sa.get("hour"),
            subject_id=sa.get("subject_id"),
            course_id=sa.get("course_id"),
            line=sa.get("line"),
        )
        session.add(support)

    session.flush()
