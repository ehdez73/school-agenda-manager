from flask import Blueprint, jsonify, request, abort
import json as _json
import logging
from sqlalchemy.orm import joinedload
from ..models import Teacher, Subject, Session, normalize_tutor_groups
from ..schemas import TeacherSchema, PreferencesSchema, DayPreferences
from ..translations import t

teachers_bp = Blueprint('teachers', __name__)
logger = logging.getLogger(__name__)

@teachers_bp.route('/teachers', methods=['GET'])
def get_teachers():
    logger.info("Listing teachers")
    session = Session()
    teachers = session.query(Teacher).options(joinedload(Teacher.subjects)).all()
    result = []
    for t in teachers:
    # prepare preferences as dict
        try:
            preferences = t.preferences and t.preferences.strip() and __import__('json').loads(t.preferences) or {}
        except Exception:
            preferences = {}
        tutor_groups = normalize_tutor_groups(t.tutor_group)
        t_dict = {
            'id': t.id,
            'name': t.name,
            'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})", 'course_id': s.course_id} for s in t.subjects],
            'max_hours_week': t.max_hours_week,
            'preferences': preferences,
            'tutor_group': tutor_groups[0] if tutor_groups else None,
            'tutor_groups': tutor_groups,
        }
        result.append(TeacherSchema(**t_dict).model_dump())
    session.close()
    logger.info("Listed teachers count=%d", len(result))
    return jsonify(result)

@teachers_bp.route('/teachers', methods=['POST'])
def add_teacher():
    data = request.get_json()
    if not data or 'name' not in data:
        logger.warning("Create teacher rejected due to missing name")
        abort(400, description=t('errors.missing_field', field='name'))
    subject_ids = data.get('subjects', [])
    session = Session()
    subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    max_hours_week = data.get('max_hours_week', 1)
    try:
        max_hours_week = int(max_hours_week)
    except (ValueError, TypeError):
        max_hours_week = 1
    if max_hours_week < 1:
        logger.warning("Create teacher rejected due to invalid max_hours_week value=%s", data.get('max_hours_week'))
        abort(400, description=t('errors.invalid_max_hours'))
    ut_raw = data.get('preferences', {})
    try:
    # PreferencesSchema validates plain dicts and exposes `.root`
        prefs_model = PreferencesSchema.model_validate(ut_raw) if ut_raw is not None else PreferencesSchema()
        ut = prefs_model.root
    # normalize to plain python types: map day index (int) -> {'unavailable': [...], 'preferred': [...]}
        normalized = {}
        for day, dp in ut.items():
            try:
                day_idx = int(day)
            except Exception:
                weekdays = t('weekdays')
                name_idx = next((i for i, name in enumerate(weekdays) if str(name).strip().lower() == str(day).strip().lower()), None)
                if name_idx is None:
                    continue
                day_idx = name_idx
            # dp is a DayPreferences model; extract lists of ints and dedupe/sort
            unavailable = sorted(list({int(x) for x in dp.unavailable}))
            preferred = sorted(list({int(x) for x in dp.preferred}))
            normalized[day_idx] = {'unavailable': unavailable, 'preferred': preferred}
        ut = normalized
    except Exception:
        session.close()
        logger.warning("Create teacher rejected due to invalid preferences")
        abort(400, description=t('errors.invalid_preferences'))

    tutor_groups = normalize_tutor_groups(data.get('tutor_groups', data.get('tutor_group')))

    new_teacher = Teacher(
        name=data['name'],
        subjects=subjects,
        max_hours_week=max_hours_week
    )
    new_teacher.set_tutor_groups(tutor_groups)
    new_teacher.preferences = _json.dumps(ut)
    session.add(new_teacher)
    session.commit()
    logger.info("Created teacher id=%s name=%s", new_teacher.id, new_teacher.name)
    response_data = TeacherSchema(**{
        'id': new_teacher.id,
        'name': new_teacher.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in new_teacher.subjects],
        'max_hours_week': new_teacher.max_hours_week,
        'preferences': ut,
        'tutor_group': tutor_groups[0] if tutor_groups else None,
        'tutor_groups': tutor_groups,
    }).model_dump()
    session.close()
    return jsonify(response_data), 201

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    logger.info("Fetching teacher id=%s", teacher_id)
    session = Session()
    teacher = session.get(Teacher, teacher_id)
    session.close()
    if teacher is None:
        logger.warning("Teacher not found id=%s", teacher_id)
        abort(404, description=t('errors.not_found', entity='Teacher', id=teacher_id))
    try:
        ut = teacher.preferences and teacher.preferences.strip() and _json.loads(teacher.preferences) or {}
    except Exception:
        ut = {}
    t_dict = {
        'id': teacher.id,
        'name': teacher.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in teacher.subjects],
        'max_hours_week': teacher.max_hours_week,
        'preferences': ut,
        'tutor_group': normalize_tutor_groups(teacher.tutor_group)[0] if normalize_tutor_groups(teacher.tutor_group) else None,
        'tutor_groups': normalize_tutor_groups(teacher.tutor_group),
    }
    return jsonify(TeacherSchema(**t_dict).model_dump())

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    data = request.get_json()
    if not data:
        logger.warning("Update teacher rejected due to missing payload id=%s", teacher_id)
        abort(400, description=t('errors.no_data_provided'))
    session = Session()
    teacher = session.get(Teacher, teacher_id)
    if teacher is None:
        session.close()
        logger.warning("Teacher not found for update id=%s", teacher_id)
        abort(404, description=t('errors.not_found', entity='Teacher', id=teacher_id))
    teacher.name = data.get('name', teacher.name)
    if 'max_hours_week' in data:
        try:
            wh = int(data['max_hours_week'])
        except (ValueError, TypeError):
            wh = 1
        if wh < 1:
            session.close()
            logger.warning("Update teacher rejected due to invalid max_hours_week id=%s", teacher_id)
            abort(400, description=t('errors.invalid_max_hours'))
        teacher.max_hours_week = wh
    subject_ids = data.get('subjects', None)
    if subject_ids is not None:
        teacher.subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
    if 'tutor_groups' in data or 'tutor_group' in data:
        teacher.set_tutor_groups(data.get('tutor_groups', data.get('tutor_group')))
    if 'preferences' in data:
        ut_raw = data.get('preferences', {})
        try:
            prefs_model = PreferencesSchema.model_validate(ut_raw) if ut_raw is not None else PreferencesSchema()
            ut = prefs_model.root
            normalized = {}
            for day, dp in ut.items():
                try:
                    day_idx = int(day)
                except Exception:
                    weekdays = t('weekdays')
                    name_idx = next((i for i, name in enumerate(weekdays) if str(name).strip().lower() == str(day).strip().lower()), None)
                    if name_idx is None:
                        continue
                    day_idx = name_idx
                unavailable = sorted(list({int(x) for x in dp.unavailable}))
                preferred = sorted(list({int(x) for x in dp.preferred}))
                normalized[day_idx] = {'unavailable': unavailable, 'preferred': preferred}
            teacher.preferences = _json.dumps(normalized)
        except Exception:
            session.close()
            logger.warning("Update teacher rejected due to invalid preferences id=%s", teacher_id)
            abort(400, description=t('errors.invalid_preferences'))
    session.commit()
    logger.info("Updated teacher id=%s", teacher.id)
    response_data = TeacherSchema(**{
        'id': teacher.id,
        'name': teacher.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in teacher.subjects],
        'max_hours_week': teacher.max_hours_week
    ,
        'tutor_group': normalize_tutor_groups(teacher.tutor_group)[0] if normalize_tutor_groups(teacher.tutor_group) else None,
        'tutor_groups': normalize_tutor_groups(teacher.tutor_group),
    }).model_dump()
    session.close()
    return jsonify(response_data)

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    logger.info("Deleting teacher id=%s", teacher_id)
    session = Session()
    teacher = session.get(Teacher, teacher_id)
    if teacher is None:
        session.close()
        logger.warning("Teacher not found for delete id=%s", teacher_id)
        abort(404, description=t('errors.not_found', entity='Teacher', id=teacher_id))
    session.delete(teacher)
    session.commit()
    session.close()
    logger.info("Deleted teacher id=%s", teacher_id)
    return jsonify({"message": t('success.deleted', entity='Teacher', id=teacher_id)}), 200
