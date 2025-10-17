from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from ..models import Subject, Course, Session, TimeSlotAssignment
from ..schemas import SubjectSchema
from ..translations import t
from sqlalchemy.orm import joinedload

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/subjects", methods=["GET"])
def get_subjects():
    session = Session()
    subjects = session.query(Subject).options(joinedload(Subject.course)).all()
    result = [SubjectSchema(**s.to_dict()).model_dump() for s in subjects]
    session.close()
    return jsonify(result)


@subjects_bp.route("/subjects", methods=["POST"])
def add_subject():
    data = request.get_json()
    if not data or "id" not in data or "name" not in data:
        abort(400, description=t("errors.missing_required_data"))
    weekly_hours = data.get("weekly_hours", 2)
    try:
        weekly_hours = int(weekly_hours)
    except (ValueError, TypeError):
        weekly_hours = 1
    max_hours_per_day = data.get("max_hours_per_day", 1)
    try:
        max_hours_per_day = int(max_hours_per_day)
    except (ValueError, TypeError):
        max_hours_per_day = 2
    course_id = data.get("course_id")
    consecutive_hours = data.get("consecutive_hours", True)
    teach_every_day = bool(data.get("teach_every_day", False))
    session = Session()
    course = session.get(Course, course_id) if course_id else None
    new_subject = Subject(
        id=data["id"],
        name=data["name"],
        weekly_hours=weekly_hours,
        max_hours_per_day=max_hours_per_day,
        consecutive_hours=bool(consecutive_hours),
        teach_every_day=teach_every_day,
        course=course,
    )
    session.add(new_subject)
    session.commit()
    response_data = SubjectSchema(**new_subject.to_dict()).model_dump()
    session.close()
    return jsonify(response_data), 201


@subjects_bp.route("/subjects/<int:subject_id>", methods=["GET"])
@subjects_bp.route("/subjects/<string:subject_id>", methods=["GET"])
def get_subject(subject_id):
    session = Session()
    subject = session.get(Subject, subject_id)
    session.close()
    if subject is None:
        abort(404, description=t("errors.not_found", id=subject_id))
    return jsonify(SubjectSchema(**subject.to_dict()).model_dump())


@subjects_bp.route("/subjects/<int:subject_id>", methods=["PUT"])
@subjects_bp.route("/subjects/<string:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    data = request.get_json()
    if not data:
        abort(400, description=t("errors.missing_name"))
    session = Session()
    subject = session.get(Subject, subject_id)
    if subject is None:
        session.close()
        abort(404, description=t("errors.not_found", id=subject_id))
    subject.name = data.get("name", subject.name)
    if "id" in data and data["id"]:
        subject.id = data["id"]
    if "weekly_hours" in data:
        # Prevent modifying weekly_hours if subject belongs to any SubjectGroup
        if getattr(subject, "subject_groups", None) and len(subject.subject_groups) > 0:
            session.close()
            abort(400, description=t("errors.hours_mismatch"))
        try:
            subject.weekly_hours = int(data["weekly_hours"])
        except (ValueError, TypeError):
            pass
    if "max_hours_per_day" in data:
        try:
            subject.max_hours_per_day = int(data["max_hours_per_day"])
        except (ValueError, TypeError):
            pass
    if "consecutive_hours" in data:
        try:
            subject.consecutive_hours = bool(data["consecutive_hours"])
        except Exception:
            pass
    if "teach_every_day" in data:
        try:
            subject.teach_every_day = bool(data["teach_every_day"])
        except Exception:
            pass
    course_id = data.get("course_id", None)
    if course_id is not None:
        subject.course = session.get(Course, course_id)
    session.commit()
    response_data = SubjectSchema(**subject.to_dict()).model_dump()
    session.close()
    return jsonify(response_data)


@subjects_bp.route("/subjects/<int:subject_id>", methods=["DELETE"])
@subjects_bp.route("/subjects/<string:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    session = Session()
    subject = session.get(Subject, subject_id)
    if subject is None:
        session.close()
        abort(404, description=t("errors.not_found", id=subject_id))
    session.query(TimeSlotAssignment).filter_by(subject_id=subject_id).delete()
    session.delete(subject)
    session.commit()
    session.close()
    return jsonify({"message": t("success.deleted", id=subject_id)}), 200
