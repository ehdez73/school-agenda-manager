from flask import Blueprint, jsonify, request, abort
import json as _json
from sqlalchemy.orm import joinedload
from ..models import Teacher, Subject, Session
from ..schemas import TeacherSchema, PreferencesSchema, DayPreferences
from ..translations import t

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/teachers', methods=['GET'])
def get_teachers():
    session = Session()
    teachers = session.query(Teacher).options(joinedload(Teacher.subjects)).all()
    result = []
    for t in teachers:
    # prepare preferences as dict
        try:
            preferences = t.preferences and t.preferences.strip() and __import__('json').loads(t.preferences) or {}
        except Exception:
            preferences = {}
        t_dict = {
            'id': t.id,
            'name': t.name,
            'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in t.subjects],
            'max_hours_week': t.max_hours_week,
            'preferences': preferences,
            'tutor_group': t.tutor_group
        }
        result.append(TeacherSchema(**t_dict).model_dump())
    session.close()
    return jsonify(result)

@teachers_bp.route('/teachers', methods=['POST'])
def add_teacher():
    data = request.get_json()
    if not data or 'name' not in data:
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
        abort(400, description=t('errors.invalid_preferences'))

    new_teacher = Teacher(
        name=data['name'],
        subjects=subjects,
        max_hours_week=max_hours_week
    )
    # optional tutor_group string like '1ºA'
    if 'tutor_group' in data:
        tg = data.get('tutor_group')
        new_teacher.tutor_group = tg if tg is not None else None
    new_teacher.preferences = _json.dumps(ut)
    session.add(new_teacher)
    session.commit()
    response_data = TeacherSchema(**{
        'id': new_teacher.id,
        'name': new_teacher.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in new_teacher.subjects],
        'max_hours_week': new_teacher.max_hours_week,
    'preferences': ut,
    'tutor_group': new_teacher.tutor_group
    }).model_dump()
    session.close()
    return jsonify(response_data), 201

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    session = Session()
    teacher = session.get(Teacher, teacher_id)
    session.close()
    if teacher is None:
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
        'tutor_group': teacher.tutor_group
    }
    return jsonify(TeacherSchema(**t_dict).model_dump())

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    data = request.get_json()
    if not data:
        abort(400, description=t('errors.no_data_provided'))
    session = Session()
    teacher = session.get(Teacher, teacher_id)
    if teacher is None:
        session.close()
        abort(404, description=t('errors.not_found', entity='Teacher', id=teacher_id))
    teacher.name = data.get('name', teacher.name)
    if 'max_hours_week' in data:
        try:
            wh = int(data['max_hours_week'])
        except (ValueError, TypeError):
            wh = 1
        if wh < 1:
            session.close()
            abort(400, description=t('errors.invalid_max_hours'))
        teacher.max_hours_week = wh
    subject_ids = data.get('subjects', None)
    if subject_ids is not None:
        teacher.subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
    if 'tutor_group' in data:
        teacher.tutor_group = data.get('tutor_group') if data.get('tutor_group') is not None else None
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
            abort(400, description=t('errors.invalid_preferences'))
    session.commit()
    response_data = TeacherSchema(**{
        'id': teacher.id,
        'name': teacher.name,
        'subjects': [{'id': s.id, 'name': s.name, 'full_name': f"{s.name} ({s.course_id})"} for s in teacher.subjects],
        'max_hours_week': teacher.max_hours_week
    ,
    'tutor_group': teacher.tutor_group
    }).model_dump()
    session.close()
    return jsonify(response_data)

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    session = Session()
    teacher = session.get(Teacher, teacher_id)
    if teacher is None:
        session.close()
        abort(404, description=t('errors.not_found', entity='Teacher', id=teacher_id))
    session.delete(teacher)
    session.commit()
    session.close()
    return jsonify({"message": t('success.deleted', entity='Teacher', id=teacher_id)}), 200
