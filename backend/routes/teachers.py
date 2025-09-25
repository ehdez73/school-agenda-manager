from flask import Blueprint, jsonify, request, abort
from models import Teacher, Subject, Session
from sqlalchemy.orm import joinedload

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/teachers', methods=['GET'])
def get_teachers():
    session = Session()
    teachers = session.query(Teacher).options(joinedload(Teacher.subjects)).all()
    result = [t.to_dict() for t in teachers]
    session.close()
    return jsonify(result)

@teachers_bp.route('/teachers', methods=['POST'])
def add_teacher():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description="Missing required field 'name'")
    subject_ids = data.get('subjects', [])
    session = Session()
    subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    weekly_hours = data.get('weekly_hours', 1)
    try:
        weekly_hours = int(weekly_hours)
    except (ValueError, TypeError):
        weekly_hours = 1
    if weekly_hours < 1:
        abort(400, description="weekly_hours debe ser un número positivo")
    new_teacher = Teacher(
        name=data['name'],
        subjects=subjects,
        restrictions=data.get('restrictions', ''),
        preferences=data.get('preferences', ''),
        weekly_hours=weekly_hours
    )
    session.add(new_teacher)
    session.commit()
    response_data = new_teacher.to_dict()
    session.close()
    return jsonify(response_data), 201

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    session = Session()
    teacher = session.query(Teacher).get(teacher_id)
    session.close()
    if teacher is None:
        abort(404, description=f"Teacher con ID {teacher_id} no encontrado")
    return jsonify(teacher.to_dict())

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    data = request.get_json()
    if not data:
        abort(400, description="No se proporcionaron datos para actualizar")
    session = Session()
    teacher = session.query(Teacher).get(teacher_id)
    if teacher is None:
        session.close()
        abort(404, description=f"Teacher con ID {teacher_id} no encontrado")
    teacher.name = data.get('name', teacher.name)
    teacher.restrictions = data.get('restrictions', teacher.restrictions)
    teacher.preferences = data.get('preferences', teacher.preferences)
    if 'weekly_hours' in data:
        try:
            wh = int(data['weekly_hours'])
        except (ValueError, TypeError):
            wh = 1
        if wh < 1:
            session.close()
            abort(400, description="weekly_hours debe ser un número positivo")
        teacher.weekly_hours = wh
    subject_ids = data.get('subjects', None)
    if subject_ids is not None:
        teacher.subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
    session.commit()
    response_data = teacher.to_dict()
    session.close()
    return jsonify(response_data)

@teachers_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    session = Session()
    teacher = session.query(Teacher).get(teacher_id)
    if teacher is None:
        session.close()
        abort(404, description=f"Teacher con ID {teacher_id} no encontrado")
    session.delete(teacher)
    session.commit()
    session.close()
    return jsonify({"message": f"Teacher con ID {teacher_id} eliminado correctamente"}), 200
