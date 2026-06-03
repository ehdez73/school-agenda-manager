import json as _json
import logging
from flask import Blueprint, jsonify, request, abort
from ..models import (
    Session,
    Teacher,
    Subject,
    Course,
    Timeslot,
    TimeSlotAssignment,
    TeacherBusySlot,
    SupportAssignment,
    Config,
)
from ..translations import t

support_bp = Blueprint("support_bp", __name__)
logger = logging.getLogger(__name__)


@support_bp.route("/timetable/gaps", methods=["GET"])
def get_gap_subjects():
    teacher_name = request.args.get("teacher_name")
    day = request.args.get("day")
    hour = request.args.get("hour")

    if not all([teacher_name, day is not None, hour is not None]):
        abort(400, description="teacher_name, day, and hour are required")

    day = int(day)
    hour = int(hour)

    session = Session()
    try:
        teacher = session.query(Teacher).filter_by(name=teacher_name).first()
        if not teacher:
            abort(404, description=t("errors.not_found", entity="Teacher", id=teacher_name))

        # Get hour label from config
        cfg = session.query(Config).first()
        hour_label = None
        if cfg and cfg.hour_names:
            try:
                names = _json.loads(cfg.hour_names)
                if isinstance(names, list) and hour < len(names):
                    hour_label = names[hour]
            except (ValueError, TypeError):
                pass

        # Find existing support for this slot (needed even for unavailable slots
        # so the frontend can show the Remove button)
        existing = (
            session.query(SupportAssignment)
            .filter_by(teacher_id=teacher.id, day=day, hour=hour)
            .first()
        )
        existing_support = None
        if existing:
            existing_support = {
                "id": existing.id,
                "subject_id": existing.subject_id,
                "subject_name": existing.subject.name,
                "course_id": existing.course_id,
                "line": existing.line,
                "course_line": f"{existing.course_id}{chr(ord('A') + existing.line)}",
            }

        # Check if this slot is marked as unavailable in teacher preferences
        prefs = {}
        if teacher.preferences:
            try:
                prefs = _json.loads(teacher.preferences)
            except (ValueError, TypeError):
                pass
        day_prefs = prefs.get(str(day), {})
        if isinstance(day_prefs, dict) and hour in day_prefs.get("unavailable", []):
            return jsonify({
                "teacher_name": teacher.name,
                "teacher_id": teacher.id,
                "day": day,
                "hour": hour,
                "hour_label": hour_label,
                "existing_support": existing_support,
                "available_subjects": [],
                "unavailable": True,
            })

        # Find all subjects being taught at this (day, hour) across all courses
        timeslots = (
            session.query(Timeslot)
            .filter_by(day=day, hour=hour)
            .all()
        )
        seen = set()
        available_subjects = []
        for ts in timeslots:
            for assign in ts.timeslot_assignments:
                key = (assign.subject_id, ts.course_id, ts.line)
                if key in seen:
                    continue
                seen.add(key)
                course_line = f"{ts.course_id}{chr(ord('A') + ts.line)}"
                available_subjects.append({
                    "subject_id": assign.subject.id,
                    "subject_name": assign.subject.name,
                    "course_id": ts.course_id,
                    "line": ts.line,
                    "course_line": course_line,
                    "color": assign.subject.color,
                })

        # Exclude subjects that already have a support assigned for this slot
        supported_keys = set()
        existing_supports = session.query(SupportAssignment).filter_by(
            day=day, hour=hour
        ).all()
        for es in existing_supports:
            supported_keys.add((es.subject_id, es.course_id, es.line))
        available_subjects = [
            s for s in available_subjects
            if (s["subject_id"], s["course_id"], s["line"]) not in supported_keys
        ]

        return jsonify({
            "teacher_name": teacher.name,
            "teacher_id": teacher.id,
            "day": day,
            "hour": hour,
            "hour_label": hour_label,
            "existing_support": existing_support,
            "available_subjects": available_subjects,
        })
    finally:
        session.close()


@support_bp.route("/support", methods=["GET"])
def list_support_assignments():
    session = Session()
    try:
        assignments = session.query(SupportAssignment).all()
        result = []
        for sa in assignments:
            result.append({
                "id": sa.id,
                "teacher_id": sa.teacher_id,
                "teacher_name": sa.teacher.name,
                "day": sa.day,
                "hour": sa.hour,
                "subject_id": sa.subject_id,
                "subject_name": sa.subject.name,
                "course_id": sa.course_id,
                "line": sa.line,
                "course_line": f"{sa.course_id}{chr(ord('A') + sa.line)}",
                "color": sa.subject.color,
            })
        return jsonify(result)
    finally:
        session.close()


@support_bp.route("/support", methods=["POST"])
def create_support_assignment():
    data = request.get_json()
    if not data:
        abort(400, description="Request body is required")

    teacher_id = data.get("teacher_id")
    day = data.get("day")
    hour = data.get("hour")
    subject_id = data.get("subject_id")
    course_id = data.get("course_id")
    line = data.get("line")

    if any(v is None for v in [teacher_id, day, hour, subject_id, course_id, line]):
        abort(400, description="Missing required fields: teacher_id, day, hour, subject_id, course_id, line")

    session = Session()
    try:
        # Validate entities exist
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            abort(404, description=t("errors.not_found", entity="Teacher", id=teacher_id))

        # Check if this slot is marked as unavailable in teacher preferences
        prefs = {}
        if teacher.preferences:
            try:
                prefs = _json.loads(teacher.preferences)
            except (ValueError, TypeError):
                pass
        day_prefs = prefs.get(str(day), {})
        if isinstance(day_prefs, dict) and hour in day_prefs.get("unavailable", []):
            abort(400, description="Teacher is not available at this slot")

        subject = session.get(Subject, subject_id)
        if not subject:
            abort(404, description=t("errors.not_found", entity="Subject", id=subject_id))
        course = session.get(Course, course_id)
        if not course:
            abort(404, description=t("errors.not_found", entity="Course", id=course_id))

        # Check slot is actually free for this teacher
        assigned = session.query(TimeSlotAssignment).join(Timeslot).filter(
            TimeSlotAssignment.teacher_id == teacher_id,
            Timeslot.day == day,
            Timeslot.hour == hour,
        ).first()
        if assigned:
            abort(400, description="Teacher already has a regular assignment at this slot")

        busy = session.query(TeacherBusySlot).filter_by(
            teacher_id=teacher_id, day=day, hour=hour
        ).first()
        if busy:
            abort(400, description="Teacher has a coordination slot at this time")

        # Check no duplicate support for same teacher/slot
        existing = session.query(SupportAssignment).filter_by(
            teacher_id=teacher_id, day=day, hour=hour
        ).first()
        if existing:
            abort(400, description="A support assignment already exists for this teacher and slot")

        # Check no duplicate support for same class (course + line + subject)
        class_already_supported = session.query(SupportAssignment).filter_by(
            course_id=course_id, line=line, day=day, hour=hour, subject_id=subject_id
        ).first()
        if class_already_supported:
            abort(400, description=t("errors.support_already_exists"))

        support = SupportAssignment(
            teacher_id=teacher_id,
            day=day,
            hour=hour,
            subject_id=subject_id,
            course_id=course_id,
            line=line,
        )
        session.add(support)
        session.commit()

        return jsonify({
            "id": support.id,
            "teacher_id": support.teacher_id,
            "teacher_name": teacher.name,
            "day": support.day,
            "hour": support.hour,
            "subject_id": support.subject_id,
            "subject_name": subject.name,
            "course_id": support.course_id,
            "line": support.line,
            "course_line": f"{course_id}{chr(ord('A') + line)}",
            "color": subject.color,
        }), 201
    except Exception as e:
        session.rollback()
        logger.exception("Failed to create support assignment")
        abort(500, description=str(e))
    finally:
        session.close()


@support_bp.route("/support/<int:support_id>", methods=["DELETE"])
def delete_support_assignment(support_id):
    session = Session()
    try:
        support = session.get(SupportAssignment, support_id)
        if not support:
            abort(404, description=t("errors.not_found", entity="SupportAssignment", id=support_id))
        session.delete(support)
        session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        session.rollback()
        logger.exception("Failed to delete support assignment")
        abort(500, description=str(e))
    finally:
        session.close()


@support_bp.route("/support", methods=["DELETE"])
def delete_all_support_assignments():
    session = Session()
    try:
        count = session.query(SupportAssignment).delete()
        session.commit()
        logger.info("Deleted all support assignments count=%d", count)
        return jsonify({"status": "ok", "deleted": count})
    except Exception as e:
        session.rollback()
        logger.exception("Failed to delete all support assignments")
        abort(500, description=str(e))
    finally:
        session.close()
