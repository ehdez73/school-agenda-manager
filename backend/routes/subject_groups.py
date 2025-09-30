from flask import Blueprint, jsonify, request, abort
from ..models import SubjectGroup, Subject, Session
from ..schemas import SubjectGroupSchema
from ..translations import t
from sqlalchemy.orm import joinedload

subject_groups_bp = Blueprint('subject_groups', __name__)


@subject_groups_bp.route('/subject-groups', methods=['GET'])
def get_subject_groups():
    session = Session()
    groups = session.query(SubjectGroup).options(joinedload(SubjectGroup.subjects)).all()
    result = []
    for g in groups:
        g_dict = {
            'id': g.id,
            'name': g.name,
            'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in g.subjects]
        }
        result.append(SubjectGroupSchema(**g_dict).model_dump())
    session.close()
    return jsonify(result)


@subject_groups_bp.route('/subject-groups', methods=['POST'])
def add_subject_group():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description=t('errors.missing_name'))
    subject_ids = data.get('subjects', [])
    session = Session()
    subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []

    # Validación: todas las subjects deben tener el mismo weekly_hours
    if subjects:
        hours_set = set(s.weekly_hours for s in subjects)
        if len(hours_set) > 1:
            session.close()
            abort(400, description=t('errors.hours_mismatch'))

    new_group = SubjectGroup(name=data['name'], subjects=subjects)
    session.add(new_group)
    session.commit()
    response_data = SubjectGroupSchema(**{
        'id': new_group.id,
        'name': new_group.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in new_group.subjects]
    }).model_dump()
    session.close()
    return jsonify(response_data), 201


@subject_groups_bp.route('/subject-groups/<int:group_id>', methods=['GET'])
def get_subject_group(group_id):
    session = Session()
    group = session.get(SubjectGroup, group_id)
    session.close()
    if group is None:
        abort(404, description=t('errors.not_found', entity='SubjectGroup', id=group_id))
    g_dict = {
        'id': group.id,
        'name': group.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in group.subjects]
    }
    return jsonify(SubjectGroupSchema(**g_dict).model_dump())


@subject_groups_bp.route('/subject-groups/<int:group_id>', methods=['PUT'])
def update_subject_group(group_id):
    data = request.get_json()
    if not data:
        abort(400, description=t('errors.no_data_provided'))
    session = Session()
    group = session.get(SubjectGroup, group_id)
    if group is None:
        session.close()
        abort(404, description=t('errors.not_found', id=group_id))
    group.name = data.get('name', group.name)
    subject_ids = data.get('subjects', None)
    if subject_ids is not None:
        subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
        # Validación: todas las subjects deben tener el mismo weekly_hours
        if subjects:
            hours_set = set(s.weekly_hours for s in subjects)
            if len(hours_set) > 1:
                session.close()
                abort(400, description=t('errors.hours_mismatch'))
        group.subjects = subjects
    session.commit()
    response_data = SubjectGroupSchema(**{
        'id': group.id,
        'name': group.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in group.subjects]
    }).model_dump()
    session.close()
    return jsonify(response_data)


@subject_groups_bp.route('/subject-groups/<int:group_id>', methods=['DELETE'])
def delete_subject_group(group_id):
    session = Session()
    group = session.get(SubjectGroup, group_id)
    if group is None:
        session.close()
        abort(404, description=t('errors.not_found', id=group_id))
    session.delete(group)
    session.commit()
    session.close()
    return jsonify({"message": t('success.deleted', id=group_id)}), 200
