import json
import logging
import re
from flask import Blueprint, jsonify, request, abort
from ..models import SubjectGroup, Subject, Session
from ..schemas import SubjectGroupSchema
from ..translations import t
from sqlalchemy.orm import joinedload

subject_groups_bp = Blueprint('subject_groups', __name__)
logger = logging.getLogger(__name__)


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _normalize_group_color(value):
    if not isinstance(value, str):
        return "#fef3c7"
    color = value.strip()
    if not HEX_COLOR_RE.match(color):
        return "#fef3c7"
    return color.lower()


def _build_group_dict(g):
    return {
        'id': g.id,
        'name': g.name,
        'color': g.color,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in g.subjects],
        'included_lines': json.loads(g.included_lines) if g.included_lines else None,
        'shared_hours': g.shared_hours,
    }


def _validate_subjects_hours(subjects, shared_hours):
    if not subjects:
        return
    if shared_hours is not None:
        if not isinstance(shared_hours, int) or shared_hours < 1:
            abort(400, description="shared_hours must be a positive integer")
        min_hours = min(s.weekly_hours for s in subjects)
        if shared_hours > min_hours:
            abort(400, description="shared_hours exceeds minimum weekly_hours of subjects")
    else:
        hours_set = set(s.weekly_hours for s in subjects)
        if len(hours_set) > 1:
            abort(400, description=t('errors.hours_mismatch'))


@subject_groups_bp.route('/subject-groups', methods=['GET'])
def get_subject_groups():
    logger.info("Listing subject groups")
    session = Session()
    groups = session.query(SubjectGroup).options(joinedload(SubjectGroup.subjects)).all()
    result = [SubjectGroupSchema(**_build_group_dict(g)).model_dump() for g in groups]
    session.close()
    logger.info("Listed subject groups count=%d", len(result))
    return jsonify(result)


@subject_groups_bp.route('/subject-groups', methods=['POST'])
def add_subject_group():
    data = request.get_json()
    if not data or 'name' not in data:
        logger.warning("Create subject group rejected due to missing name")
        abort(400, description=t('errors.missing_name'))
    subject_ids = data.get('subjects', [])
    session = Session()
    subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []

    shared_hours = data.get('shared_hours', None)
    _validate_subjects_hours(subjects, shared_hours)

    included_lines = data.get("included_lines", None)
    if included_lines is not None:
        included_lines = json.dumps(included_lines)
    color = _normalize_group_color(data.get('color', '#fef3c7'))

    new_group = SubjectGroup(
        name=data['name'], color=color, subjects=subjects,
        included_lines=included_lines, shared_hours=shared_hours,
    )
    session.add(new_group)
    session.commit()
    logger.info("Created subject group id=%s", new_group.id)
    g_dict = _build_group_dict(new_group)
    response_data = SubjectGroupSchema(**g_dict).model_dump()
    session.close()
    return jsonify(response_data), 201


@subject_groups_bp.route('/subject-groups/<int:group_id>', methods=['GET'])
def get_subject_group(group_id):
    logger.info("Fetching subject group id=%s", group_id)
    session = Session()
    group = session.get(SubjectGroup, group_id)
    session.close()
    if group is None:
        logger.warning("Subject group not found id=%s", group_id)
        abort(404, description=t('errors.not_found', entity='SubjectGroup', id=group_id))
    g_dict = _build_group_dict(group)
    return jsonify(SubjectGroupSchema(**g_dict).model_dump())


@subject_groups_bp.route('/subject-groups/<int:group_id>', methods=['PUT'])
def update_subject_group(group_id):
    data = request.get_json()
    if not data:
        logger.warning("Update subject group rejected due to missing payload id=%s", group_id)
        abort(400, description=t('errors.no_data_provided'))
    session = Session()
    group = session.get(SubjectGroup, group_id)
    if group is None:
        session.close()
        logger.warning("Subject group not found for update id=%s", group_id)
        abort(404, description=t('errors.not_found', id=group_id))
    group.name = data.get('name', group.name)
    if 'color' in data:
        group.color = _normalize_group_color(data.get('color'))
    subject_ids = data.get('subjects', None)
    if subject_ids is not None:
        subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
        shared_hours = data.get('shared_hours', group.shared_hours)
        _validate_subjects_hours(subjects, shared_hours)
        group.subjects = subjects
        group.shared_hours = shared_hours
    elif 'shared_hours' in data:
        group.shared_hours = data.get('shared_hours')
        subjects = group.subjects
        _validate_subjects_hours(subjects, group.shared_hours)
    if "included_lines" in data:
        val = data["included_lines"]
        group.included_lines = json.dumps(val) if val is not None else None
    session.commit()
    logger.info("Updated subject group id=%s", group.id)
    g_dict = _build_group_dict(group)
    response_data = SubjectGroupSchema(**g_dict).model_dump()
    session.close()
    return jsonify(response_data)


@subject_groups_bp.route('/subject-groups/<int:group_id>', methods=['DELETE'])
def delete_subject_group(group_id):
    logger.info("Deleting subject group id=%s", group_id)
    session = Session()
    group = session.get(SubjectGroup, group_id)
    if group is None:
        session.close()
        logger.warning("Subject group not found for delete id=%s", group_id)
        abort(404, description=t('errors.not_found', id=group_id))
    session.delete(group)
    session.commit()
    session.close()
    logger.info("Deleted subject group id=%s", group_id)
    return jsonify({"message": t('success.deleted', id=group_id)}), 200
