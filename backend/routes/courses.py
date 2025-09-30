from flask import Blueprint, jsonify, request, abort
from flask_cors import CORS
from ..models import Subject, Course, Session, Timeslot, TimeSlotAssignment
from ..schemas import CourseSchema, SubjectSchema
from ..translations import t
from sqlalchemy.orm import joinedload

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/courses', methods=['GET'])
def get_courses():
    session = Session()
    courses = session.query(Course).all()
    session.close()
    return jsonify([CourseSchema(**c.to_dict()).model_dump() for c in courses])

@courses_bp.route('/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    if not data or 'name' not in data:
        abort(400, description=t('errors.missing_field', field='name'))
    num_lines = data.get('num_lines', 1)
    try:
        num_lines = int(num_lines)
    except (ValueError, TypeError):
        num_lines = 1
    new_course = Course(id=data['name'], num_lines=num_lines)
    session = Session()
    session.add(new_course)
    session.commit()
    response_data = CourseSchema(**new_course.to_dict()).model_dump()
    session.close()
    return jsonify(response_data), 201

@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
@courses_bp.route('/courses/<string:course_id>', methods=['GET'])
def get_course(course_id):
    session = Session()
    course = session.get(Course, course_id)
    session.close()
    if course is None:
        abort(404, description=t('errors.not_found', entity='Course', id=course_id))
    return jsonify(CourseSchema(**course.to_dict()).model_dump())

@courses_bp.route('/courses/<int:course_id>', methods=['PUT'])
@courses_bp.route('/courses/<string:course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json()
    if not data:
        abort(400, description=t('errors.no_data_provided'))
    session = Session()
    course = session.get(Course, course_id)
    if course is None:
        session.close()
        abort(404, description=t('errors.not_found', entity='Course', id=course_id))
    if 'name' in data and data['name']:
        course.id = data['name']
    if 'num_lines' in data:
        try:
            course.num_lines = int(data['num_lines'])
        except (ValueError, TypeError):
            pass
    subject_ids = data.get('subjects', None)
    if subject_ids is not None:
        subjects = session.query(Subject).filter(Subject.id.in_(subject_ids)).all()
        for subject in subjects:
            subject.course = course
        current_subjects = session.query(Subject).filter(Subject.course_id == course_id).all()
        for subject in current_subjects:
            if subject.id not in subject_ids:
                subject.course = None
    session.commit()
    response_data = CourseSchema(**course.to_dict()).model_dump()
    session.close()
    return jsonify(response_data)

@courses_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@courses_bp.route('/courses/<string:course_id>', methods=['DELETE'])
def delete_course(course_id):
    session = Session()
    course = session.get(Course, course_id)
    if course is None:
        session.close()
        abort(404, description=t('errors.not_found', entity='Course', id=course_id))
    timeslots = session.query(Timeslot).filter_by(course_id=course_id).all()
    for timeslot in timeslots:
        session.query(TimeSlotAssignment).filter_by(timeslot_id=timeslot.id).delete()
        session.delete(timeslot)
    session.delete(course)
    session.commit()
    session.close()
    return jsonify({"message": t('success.course_deleted', id=course_id)}), 200

@courses_bp.route('/courses/<int:course_id>/subjects', methods=['GET'])
@courses_bp.route('/courses/<string:course_id>/subjects', methods=['GET'])
def get_subjects_by_course(course_id):
    session = Session()
    course = session.get(Course, course_id)
    if course is None:
        session.close()
        abort(404, description=t('errors.not_found', entity='Course', id=course_id))
    subjects = session.query(Subject).options(joinedload(Subject.course)).filter(Subject.course_id == course_id).all()
    session.close()
    return jsonify([SubjectSchema(**s.to_dict()).model_dump() for s in subjects])
