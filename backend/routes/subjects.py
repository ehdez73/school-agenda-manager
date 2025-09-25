from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from models import Subject, Course, Session
from sqlalchemy.orm import joinedload

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/subjects', methods=['GET'])
def get_subjects():
    session = Session()
    subjects = session.query(Subject).options(joinedload(Subject.course)).all()
    result = [s.to_dict() for s in subjects]
    session.close()
    return jsonify(result)

@subjects_bp.route('/subjects', methods=['POST'])
def add_subject():
    data = request.get_json()
    if not data or 'id' not in data or 'name' not in data:
        abort(400, description="Faltan datos requeridos (id, name)")
    weekly_hours = data.get('weekly_hours', 2)
    try:
        weekly_hours = int(weekly_hours)
    except (ValueError, TypeError):
        weekly_hours = 1
    course_id = data.get('course_id')
    session = Session()
    course = session.query(Course).get(course_id) if course_id else None
    new_subject = Subject(id=data['id'], name=data['name'], weekly_hours=weekly_hours, course=course)
    session.add(new_subject)
    session.commit()
    response_data = new_subject.to_dict()
    session.close()
    return jsonify(response_data), 201

@subjects_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@subjects_bp.route('/subjects/<string:subject_id>', methods=['GET'])
def get_subject(subject_id):
    session = Session()
    subject = session.query(Subject).get(subject_id)
    session.close()
    if subject is None:
        abort(404, description=f"Subject con ID {subject_id} no encontrado")
    return jsonify(subject.to_dict())

@subjects_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@subjects_bp.route('/subjects/<string:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    
    data = request.get_json()
    if not data:
        abort(400, description="No se proporcionaron datos para actualizar")
    session = Session()
    subject = session.query(Subject).get(subject_id)
    if subject is None:
        session.close()
        abort(404, description=f"Subject con ID {subject_id} no encontrado")
    subject.name = data.get('name', subject.name)
    if 'id' in data and data['id']:
        subject.id = data['id']
    if 'weekly_hours' in data:
        try:
            subject.weekly_hours = int(data['weekly_hours'])
        except (ValueError, TypeError):
            pass
    course_id = data.get('course_id', None)
    if course_id is not None:
        subject.course = session.query(Course).get(course_id)
    session.commit()
    response_data = subject.to_dict()
    session.close()
    return jsonify(response_data)

@subjects_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@subjects_bp.route('/subjects/<string:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    session = Session()
    subject = session.query(Subject).get(subject_id)
    if subject is None:
        session.close()
        abort(404, description=f"Subject con ID {subject_id} no encontrado")
    session.delete(subject)
    session.commit()
    session.close()
    return jsonify({"message": f"Subject con ID {subject_id} eliminado correctamente"}), 200
