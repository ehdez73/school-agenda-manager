import logging

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ..models import Session as DbSession, FixedSlot, CourseFixedSlotLabel
from ..logging_config import build_log_extra
from ..schemas import CourseFixedSlotLabelUpsert

course_fixed_slot_labels_bp = Blueprint("course_fixed_slot_labels_bp", __name__)
logger = logging.getLogger(__name__)


@course_fixed_slot_labels_bp.route("/course-fixed-slot-labels", methods=["GET"])
def list_course_fixed_slot_labels():
    session = DbSession()
    try:
        course_line = request.args.get("course_line", type=str)

        query = session.query(CourseFixedSlotLabel)
        if course_line is not None:
            query = query.filter_by(course_line=course_line)

        labels = query.all()
        return jsonify([
            {
                "id": lbl.id,
                "course_line": lbl.course_line,
                "fixed_slot_id": lbl.fixed_slot_id,
                "day": lbl.day,
                "label": lbl.label,
            }
            for lbl in labels
        ])
    finally:
        session.close()


@course_fixed_slot_labels_bp.route("/course-fixed-slot-labels", methods=["POST"])
def upsert_course_fixed_slot_label():
    session = DbSession()
    try:
        body = request.get_json(silent=True) or {}
        try:
            data = CourseFixedSlotLabelUpsert(**body)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        fixed_slot = session.get(FixedSlot, data.fixed_slot_id)
        if not fixed_slot:
            return jsonify({"error": "FixedSlot not found"}), 404

        if fixed_slot.slot_type != "course":
            return jsonify({"error": "FixedSlot is not a course slot"}), 400

        existing = session.query(CourseFixedSlotLabel).filter_by(
            course_line=data.course_line,
            fixed_slot_id=data.fixed_slot_id,
            day=data.day,
        ).first()

        default_label = fixed_slot.label
        if data.label == default_label:
            if existing:
                session.delete(existing)
                session.commit()
                logger.info(
                    "Reset course fixed slot label to default "
                    "course_line=%s fixed_slot_id=%d day=%d",
                    data.course_line, data.fixed_slot_id, data.day,
                    extra=build_log_extra(),
                )
            return jsonify({"status": "reset"}), 200

        if existing:
            existing.label = data.label
        else:
            existing = CourseFixedSlotLabel(
                course_line=data.course_line,
                fixed_slot_id=data.fixed_slot_id,
                day=data.day,
                label=data.label,
            )
            session.add(existing)

        session.commit()
        logger.info(
            "Upserted course fixed slot label course_line=%s fixed_slot_id=%d day=%d label=%s",
            data.course_line, data.fixed_slot_id, data.day, data.label,
            extra=build_log_extra(),
        )
        return jsonify({
            "id": existing.id,
            "course_line": existing.course_line,
            "fixed_slot_id": existing.fixed_slot_id,
            "day": existing.day,
            "label": existing.label,
        }), 200
    finally:
        session.close()


@course_fixed_slot_labels_bp.route("/course-fixed-slot-labels", methods=["DELETE"])
def delete_course_fixed_slot_label():
    session = DbSession()
    try:
        course_line = request.args.get("course_line", type=str)
        fixed_slot_id = request.args.get("fixed_slot_id", type=int)
        day = request.args.get("day", type=int)

        if course_line is None or fixed_slot_id is None or day is None:
            return jsonify({"error": "course_line, fixed_slot_id, and day are required"}), 400

        existing = session.query(CourseFixedSlotLabel).filter_by(
            course_line=course_line,
            fixed_slot_id=fixed_slot_id,
            day=day,
        ).first()

        if not existing:
            return jsonify({"status": "not_found"}), 404

        session.delete(existing)
        session.commit()
        logger.info(
            "Deleted course fixed slot label course_line=%s fixed_slot_id=%d day=%d",
            course_line, fixed_slot_id, day,
            extra=build_log_extra(),
        )
        return jsonify({"status": "deleted"}), 200
    finally:
        session.close()
