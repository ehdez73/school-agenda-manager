import logging

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from ..models import FixedSlot, Session
from ..schemas import FixedSlotCreate, FixedSlotUpdate, FixedSlotResponse
from ..logging_config import build_log_extra
from ..translations import t


fixed_slots_bp = Blueprint("fixed_slots", __name__)
logger = logging.getLogger(__name__)


def _get_session():
    return Session()


@fixed_slots_bp.route("/fixed-slots", methods=["GET"])
def list_fixed_slots():
    session = _get_session()
    try:
        slot_type = request.args.get("type")
        q = session.query(FixedSlot).order_by(FixedSlot.position)
        if slot_type:
            q = q.filter(FixedSlot.slot_type == slot_type)
        slots = q.all()
        return jsonify([s.to_dict() for s in slots]), 200
    finally:
        session.close()


def _position_occupied(session, slot_type, position, exclude_id=None):
    q = session.query(FixedSlot).filter(
        FixedSlot.slot_type == slot_type,
        FixedSlot.position == position,
    )
    if exclude_id is not None:
        q = q.filter(FixedSlot.id != exclude_id)
    return q.first() is not None


@fixed_slots_bp.route("/fixed-slots", methods=["POST"])
def create_fixed_slot():
    try:
        data = FixedSlotCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400

    session = _get_session()
    try:
        if _position_occupied(session, data.slot_type, data.position):
            return jsonify({
                "error": "Position already occupied",
                "message": t("errors.fixed_slot_position_occupied", slot_type=data.slot_type, position=data.position),
                "field": "position",
            }), 409

        slot = FixedSlot(
            slot_type=data.slot_type,
            position=data.position,
            label=data.label,
            time_range=data.time_range,
        )
        session.add(slot)
        session.commit()
        logger.info(
            "FixedSlot created id=%s type=%s pos=%s label=%s",
            slot.id, slot.slot_type, slot.position, slot.label,
            extra=build_log_extra(),
        )
        return jsonify(slot.to_dict()), 201
    finally:
        session.close()


@fixed_slots_bp.route("/fixed-slots/<int:slot_id>", methods=["PUT"])
def update_fixed_slot(slot_id):
    session = _get_session()
    try:
        slot = session.get(FixedSlot, slot_id)
        if not slot:
            return jsonify({"error": "Not found"}), 404

        try:
            data = FixedSlotUpdate(**request.json)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        new_type = data.slot_type if data.slot_type is not None else slot.slot_type
        new_position = data.position if data.position is not None else slot.position
        if (new_type != slot.slot_type or new_position != slot.position) and \
           _position_occupied(session, new_type, new_position, exclude_id=slot_id):
            return jsonify({
                "error": "Position already occupied",
                "message": t("errors.fixed_slot_position_occupied", slot_type=new_type, position=new_position),
                "field": "position",
            }), 409

        changed = False
        for key in ("slot_type", "position", "label", "time_range"):
            val = getattr(data, key, None)
            if val is not None:
                setattr(slot, key, val)
                changed = True
        if changed:
            session.commit()
            logger.info("FixedSlot updated id=%s", slot.id, extra=build_log_extra())
        return jsonify(slot.to_dict()), 200
    finally:
        session.close()


@fixed_slots_bp.route("/fixed-slots/<int:slot_id>", methods=["DELETE"])
def delete_fixed_slot(slot_id):
    session = _get_session()
    try:
        slot = session.get(FixedSlot, slot_id)
        if not slot:
            return jsonify({"error": "Not found"}), 404
        session.delete(slot)
        session.commit()
        logger.info("FixedSlot deleted id=%s", slot_id, extra=build_log_extra())
        return "", 204
    finally:
        session.close()
