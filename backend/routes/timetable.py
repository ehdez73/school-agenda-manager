import threading

from flask import Blueprint, jsonify, request
from ..translations import t
from ..models import Session as DbSession, TimeSlotAssignment
from ..timetable import print_markdown_timetable_from_assignments, print_markdown_timetable_per_teacher
from ..markdown_utils import align_tables_in_text
from ..scheduler import create_timetable
from ..task_manager import task_manager


timetable_bp = Blueprint('timetable_bp', __name__)


def _run_solver_in_background(task_id):
    """Run the OR-Tools solver in a background thread.
    Checks cancellation before/after solve to avoid unnecessary DB writes.
    """
    if task_manager.is_cancelled(task_id):
        return

    def progress_callback(phase, phase_details):
        task_manager.update_progress(task_id, phase, phase_details)

    session = DbSession()
    try:
        timetable_result = create_timetable(session, progress_callback=progress_callback)

        if task_manager.is_cancelled(task_id):
            return

        if timetable_result:
            task_manager.fail_task(
                task_id,
                error=t('timetable.generate_failed'),
                details=timetable_result,
            )
        else:
            task_manager.complete_task(task_id)
    except Exception as e:
        if not task_manager.is_cancelled(task_id):
            task_manager.fail_task(
                task_id,
                error=t('errors.timetable_generation_error', error=str(e)),
            )


@timetable_bp.route('/api/timetable', methods=['GET'])
def get_timetable_markdown():
    session = DbSession()

    existing_assignments = session.query(TimeSlotAssignment).first()
    if not existing_assignments:
        session.close()
        return jsonify({'error': t('timetable.no_schedule')}), 404

    courses_markdown = print_markdown_timetable_from_assignments(session)
    teachers_markdown = print_markdown_timetable_per_teacher(session)
    markdown = courses_markdown + "\n\n" + teachers_markdown
    session.close()
    return markdown, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@timetable_bp.route('/api/timetable', methods=['POST'])
def generate_timetable():
    """Start asynchronous timetable generation. Returns task_id immediately."""
    task_id = task_manager.create_task()
    thread = threading.Thread(
        target=_run_solver_in_background,
        args=(task_id,),
        daemon=True,
    )
    thread.start()
    return jsonify({"task_id": task_id}), 202


@timetable_bp.route('/api/timetable/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Poll task status. Returns running/success/error/cancelled."""
    status = task_manager.get_status(task_id)
    if status is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(status), 200


@timetable_bp.route('/api/timetable/<task_id>/cancel', methods=['POST'])
def cancel_generation(task_id):
    """Mark a running generation task as cancelled."""
    task_manager.cancel_task(task_id)
    return jsonify({"status": "cancelled"}), 200


@timetable_bp.route('/api/timetable', methods=['DELETE'])
def clear_assignments():
    """Delete all timetable assignments (previously /api/assignments)."""
    from ..models import Session
    session = Session()
    session.query(TimeSlotAssignment).delete()
    session.commit()
    session.close()
    return jsonify({'status': 'ok', 'message': t('timetable.assignments_cleared')}), 200
