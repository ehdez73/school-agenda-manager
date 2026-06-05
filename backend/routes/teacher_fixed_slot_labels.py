import logging

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ..models import Session as DbSession, Teacher, FixedSlot, TeacherFixedSlotLabel
from ..logging_config import build_log_extra
from ..schemas import TeacherFixedSlotLabelUpsert

teacher_fixed_slot_labels_bp = Blueprint("teacher_fixed_slot_labels_bp", __name__)
logger = logging.getLogger(__name__)


@teacher_fixed_slot_labels_bp.route("/teacher-fixed-slot-labels", methods=["GET"])
def list_teacher_fixed_slot_labels():
    session = DbSession()
    try:
        teacher_id = request.args.get("teacher_id", type=int)

        query = session.query(TeacherFixedSlotLabel)
        if teacher_id is not None:
            query = query.filter_by(teacher_id=teacher_id)

        labels = query.all()
        return jsonify([
            {
                "id": lbl.id,
                "teacher_id": lbl.teacher_id,
                "fixed_slot_id": lbl.fixed_slot_id,
                "day": lbl.day,
                "label": lbl.label,
            }
            for lbl in labels
        ])
    finally:
        session.close()


@teacher_fixed_slot_labels_bp.route("/teacher-fixed-slot-labels", methods=["POST"])
def upsert_teacher_fixed_slot_label():
    session = DbSession()
    try:
        body = request.get_json(silent=True) or {}
        try:
            data = TeacherFixedSlotLabelUpsert(**body)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        teacher = session.get(Teacher, data.teacher_id)
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404

        fixed_slot = session.get(FixedSlot, data.fixed_slot_id)
        if not fixed_slot:
            return jsonify({"error": "FixedSlot not found"}), 404

        if fixed_slot.slot_type != "teacher":
            return jsonify({"error": "FixedSlot is not a teacher slot"}), 400

        existing = session.query(TeacherFixedSlotLabel).filter_by(
            teacher_id=data.teacher_id,
            fixed_slot_id=data.fixed_slot_id,
            day=data.day,
        ).first()

        default_label = fixed_slot.label
        if data.label == default_label:
            # Resetting to default – remove the override
            if existing:
                session.delete(existing)
                session.commit()
                logger.info(
                    "Reset teacher fixed slot label to default "
                    "teacher_id=%d fixed_slot_id=%d day=%d",
                    data.teacher_id, data.fixed_slot_id, data.day,
                    extra=build_log_extra(),
                )
            return jsonify({"status": "reset"}), 200

        if existing:
            existing.label = data.label
        else:
            existing = TeacherFixedSlotLabel(
                teacher_id=data.teacher_id,
                fixed_slot_id=data.fixed_slot_id,
                day=data.day,
                label=data.label,
            )
            session.add(existing)

        session.commit()
        logger.info(
            "Upserted teacher fixed slot label teacher_id=%d fixed_slot_id=%d day=%d label=%s",
            data.teacher_id, data.fixed_slot_id, data.day, data.label,
            extra=build_log_extra(),
        )
        return jsonify({
            "id": existing.id,
            "teacher_id": existing.teacher_id,
            "fixed_slot_id": existing.fixed_slot_id,
            "day": existing.day,
            "label": existing.label,
        }), 200
    finally:
        session.close()


@teacher_fixed_slot_labels_bp.route("/teacher-fixed-slot-labels", methods=["DELETE"])
def delete_teacher_fixed_slot_label():
    session = DbSession()
    try:
        teacher_id = request.args.get("teacher_id", type=int)
        fixed_slot_id = request.args.get("fixed_slot_id", type=int)
        day = request.args.get("day", type=int)

        if teacher_id is None or fixed_slot_id is None or day is None:
            return jsonify({"error": "teacher_id, fixed_slot_id, and day are required"}), 400

        existing = session.query(TeacherFixedSlotLabel).filter_by(
            teacher_id=teacher_id,
            fixed_slot_id=fixed_slot_id,
            day=day,
        ).first()

        if not existing:
            return jsonify({"status": "not_found"}), 404

        session.delete(existing)
        session.commit()
        logger.info(
            "Deleted teacher fixed slot label teacher_id=%d fixed_slot_id=%d day=%d",
            teacher_id, fixed_slot_id, day,
            extra=build_log_extra(),
        )
        return jsonify({"status": "deleted"}), 200
    finally:
        session.close()
