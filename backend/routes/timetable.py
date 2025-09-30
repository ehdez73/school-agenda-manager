from flask import Blueprint, jsonify, request
from ..translations import t
from ..models import Session, TimeSlotAssignment
from ..timetable import print_markdown_timetable_from_assignments, print_markdown_timetable_per_teacher
from ..markdown_utils import align_tables_in_text
from ..scheduler import create_timetable


timetable_bp = Blueprint('timetable_bp', __name__)


@timetable_bp.route('/api/timetable', methods=['GET'])
def get_timetable_markdown():
    session = Session()

    existing_assignments = session.query(TimeSlotAssignment).first()
    if not existing_assignments:
        session.close()
        return jsonify({'error': t('timetable.no_schedule')}), 404

    courses_markdown = print_markdown_timetable_from_assignments(session)
    teachers_markdown = print_markdown_timetable_per_teacher(session)
    markdown = courses_markdown + "\n\n" + teachers_markdown
    markdown = align_tables_in_text(markdown)
    session.close()
    return markdown, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@timetable_bp.route('/api/timetable', methods=['POST'])
def generate_timetable():
    """Generate a new timetable using the scheduler"""
    session = Session()
    
    try:
        timetable_result = create_timetable(session)
        if timetable_result:
            # If create_timetable returns markdown with unsatisfied restrictions
            session.close()
            return jsonify({'error': t('timetable.generate_failed'), 'details': timetable_result}), 400
        else:
            session.close()
            return jsonify({'status': 'success', 'message': t('timetable.generated_success')}), 200
    except Exception as e:
        session.close()
        return jsonify({'error': t('errors.timetable_generation_error', error=str(e))}), 500


@timetable_bp.route('/api/timetable', methods=['DELETE'])
def clear_assignments():
    """Delete all timetable assignments (previously /api/assignments)."""
    session = Session()
    session.query(TimeSlotAssignment).delete()
    session.commit()
    session.close()
    return jsonify({'status': 'ok', 'message': t('timetable.assignments_cleared')}), 200
