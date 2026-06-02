import json
import logging
from flask import Blueprint, jsonify, request, abort
from ..models import JointClass, Subject, Teacher, Course, Session
from ..schemas import JointClassSchema
from ..translations import t
from sqlalchemy.orm import joinedload

joint_classes_bp = Blueprint("joint_classes", __name__)
logger = logging.getLogger(__name__)


def _build_jc_dict(jc):
    return {
        "id": jc.id,
        "name": jc.name,
        "course_id": jc.course_id,
        "subject_id": jc.subject_id,
        "teacher_id": jc.teacher_id,
        "lines": json.loads(jc.lines) if jc.lines else [],
        "shared_hours": jc.shared_hours,
        "course": jc.course.to_dict() if jc.course else None,
        "subject": jc.subject.to_dict() if jc.subject else None,
        "teacher": jc.teacher.to_dict() if jc.teacher else None,
    }


@joint_classes_bp.route("/joint-classes", methods=["GET"])
def get_joint_classes():
    logger.info("Listing joint classes")
    session = Session()
    items = (
        session.query(JointClass)
        .options(joinedload(JointClass.course), joinedload(JointClass.subject), joinedload(JointClass.teacher))
        .all()
    )
    result = [JointClassSchema(**_build_jc_dict(jc)).model_dump() for jc in items]
    session.close()
    logger.info("Listed joint classes count=%d", len(result))
    return jsonify(result)


@joint_classes_bp.route("/joint-classes", methods=["POST"])
def add_joint_class():
    data = request.get_json()
    if not data:
        abort(400, description=t("errors.missing_required_data"))
    if "course_id" not in data or "subject_id" not in data:
        abort(400, description=t("errors.missing_required_data"))
    lines = data.get("lines", [])
    if not isinstance(lines, list) or len(lines) < 2:
        abort(400, description=t("At least 2 lines are required for a joint class"))
    session = Session()
    course = session.get(Course, data["course_id"])
    if not course:
        session.close()
        abort(400, description=t("errors.not_found", entity="Course", id=data["course_id"]))
    subject = session.get(Subject, data["subject_id"])
    if not subject:
        session.close()
        abort(400, description=t("errors.not_found", entity="Subject", id=data["subject_id"]))
    teacher = None
    teacher_id = data.get("teacher_id")
    if teacher_id is not None:
        teacher = session.get(Teacher, teacher_id)
        if not teacher:
            session.close()
            abort(400, description=t("errors.not_found", entity="Teacher", id=teacher_id))
    shared_hours = data.get("shared_hours", None)
    new_jc = JointClass(
        name=data.get("name"),
        course_id=data["course_id"],
        subject_id=data["subject_id"],
        teacher_id=teacher_id,
        lines=json.dumps(lines),
        shared_hours=shared_hours,
    )
    session.add(new_jc)
    session.commit()
    # Re-query with relationships for the response
    session.refresh(new_jc)
    jc = (
        session.query(JointClass)
        .options(joinedload(JointClass.course), joinedload(JointClass.subject), joinedload(JointClass.teacher))
        .filter(JointClass.id == new_jc.id)
        .first()
    )
    response_data = JointClassSchema(**{**_build_jc_dict(jc)}).model_dump()
    session.close()
    logger.info("Created joint class id=%s", new_jc.id)
    return jsonify(response_data), 201


@joint_classes_bp.route("/joint-classes/<int:jc_id>", methods=["GET"])
def get_joint_class(jc_id):
    logger.info("Fetching joint class id=%s", jc_id)
    session = Session()
    jc = (
        session.query(JointClass)
        .options(joinedload(JointClass.course), joinedload(JointClass.subject), joinedload(JointClass.teacher))
        .filter(JointClass.id == jc_id)
        .first()
    )
    session.close()
    if jc is None:
        abort(404, description=t("errors.not_found", entity="JointClass", id=jc_id))
    return jsonify(JointClassSchema(**{**_build_jc_dict(jc)}).model_dump())


@joint_classes_bp.route("/joint-classes/<int:jc_id>", methods=["PUT"])
def update_joint_class(jc_id):
    data = request.get_json()
    if not data:
        abort(400, description=t("errors.no_data_provided"))
    session = Session()
    jc = (
        session.query(JointClass)
        .options(joinedload(JointClass.course), joinedload(JointClass.subject), joinedload(JointClass.teacher))
        .filter(JointClass.id == jc_id)
        .first()
    )
    if jc is None:
        session.close()
        abort(404, description=t("errors.not_found", id=jc_id))
    if "name" in data:
        jc.name = data["name"]
    if "course_id" in data:
        jc.course_id = data["course_id"]
    if "subject_id" in data:
        jc.subject_id = data["subject_id"]
    if "teacher_id" in data:
        jc.teacher_id = data["teacher_id"]
    if "lines" in data:
        jc.lines = json.dumps(data["lines"]) if isinstance(data["lines"], list) else jc.lines
    if "shared_hours" in data:
        jc.shared_hours = data["shared_hours"]
    session.commit()
    session.refresh(jc)
    response_data = JointClassSchema(**{**_build_jc_dict(jc)}).model_dump()
    session.close()
    logger.info("Updated joint class id=%s", jc.id)
    return jsonify(response_data)


@joint_classes_bp.route("/joint-classes/<int:jc_id>", methods=["DELETE"])
def delete_joint_class(jc_id):
    logger.info("Deleting joint class id=%s", jc_id)
    session = Session()
    jc = session.get(JointClass, jc_id)
    if jc is None:
        session.close()
        abort(404, description=t("errors.not_found", id=jc_id))
    session.delete(jc)
    session.commit()
    session.close()
    logger.info("Deleted joint class id=%s", jc_id)
    return jsonify({"message": t("success.deleted", entity="JointClass", id=jc_id)}), 200
