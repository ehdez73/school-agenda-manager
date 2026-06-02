import threading
import logging
from datetime import datetime

from flask import Blueprint, jsonify
from ..translations import t
from ..models import Session as DbSession, TimeSlotAssignment, SchedulerError
from ..timetable import print_markdown_timetable_from_assignments, print_markdown_timetable_per_teacher
from ..markdown_utils import align_tables_in_text
from ..scheduler import create_timetable
from ..task_manager import task_manager
from ..logging_config import build_log_extra
from ..translations import get_current_locale


timetable_bp = Blueprint('timetable_bp', __name__)
logger = logging.getLogger(__name__)


def _persist_scheduler_error(message, details):
    """Save or update the single-row scheduler error in the database."""
    session = DbSession()
    try:
        error = session.query(SchedulerError).filter_by(id=1).first()
        if error:
            error.message = message
            error.details = details
            error.created_at = datetime.now().isoformat()
        else:
            error = SchedulerError(
                id=1,
                message=message,
                details=details,
                created_at=datetime.now().isoformat(),
            )
            session.add(error)
        session.commit()
        logger.info("Persisted scheduler error: %s", message)
    except Exception as e:
        logger.exception("Failed to persist scheduler error: %s", e)
        session.rollback()
    finally:
        session.close()


def _clear_scheduler_error():
    """Remove the persisted scheduler error from the database."""
    session = DbSession()
    try:
        session.query(SchedulerError).filter_by(id=1).delete()
        session.commit()
        logger.info("Cleared persisted scheduler error")
    except Exception as e:
        logger.exception("Failed to clear scheduler error: %s", e)
        session.rollback()
    finally:
        session.close()


def _run_solver_in_background(task_id, locale):
    """Run the OR-Tools solver in a background thread.
    Checks cancellation before/after solve to avoid unnecessary DB writes.
    """
    if task_manager.is_cancelled(task_id):
        logger.info("Skipping solver start because task was already cancelled", extra=build_log_extra(task_id=task_id))
        return

    def progress_callback(phase, phase_details):
        task_manager.update_progress(task_id, phase, phase_details)
        logger.info(
            "Task progress updated phase=%s details_length=%d",
            phase,
            len(phase_details or ""),
            extra=build_log_extra(task_id=task_id),
        )

    session = DbSession()
    logger.info("Background solver thread started", extra=build_log_extra(task_id=task_id))
    try:
        timetable_result = create_timetable(
            session,
            progress_callback=progress_callback,
            task_id=task_id,
            locale=locale,
        )

        if task_manager.is_cancelled(task_id):
            logger.info("Task cancelled after solver completion", extra=build_log_extra(task_id=task_id))
            return

        if timetable_result:
            task_manager.fail_task(
                task_id,
                error=t('timetable.generate_failed'),
                details=timetable_result,
            )
            _persist_scheduler_error(
                message=t('timetable.generate_failed'),
                details=timetable_result,
            )
            logger.warning("Task failed with diagnostic output", extra=build_log_extra(task_id=task_id))
        else:
            task_manager.complete_task(task_id)
            _clear_scheduler_error()
            logger.info("Task completed successfully", extra=build_log_extra(task_id=task_id))
    except Exception as e:
        if not task_manager.is_cancelled(task_id):
            task_manager.fail_task(
                task_id,
                error=t('errors.timetable_generation_error', error=str(e)),
            )
            _persist_scheduler_error(
                message=t('errors.timetable_generation_error', error=str(e)),
                details=None,
            )
            logger.exception("Task failed with unexpected exception", extra=build_log_extra(task_id=task_id))
    finally:
        try:
            session.close()
        except Exception:
            pass
        logger.info("Background solver thread finished", extra=build_log_extra(task_id=task_id))


@timetable_bp.route('/timetable', methods=['GET'])
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


@timetable_bp.route('/timetable/error', methods=['GET'])
def get_persisted_error():
    """Return the persisted scheduler error (survives server restarts)."""
    session = DbSession()
    try:
        error = session.query(SchedulerError).filter_by(id=1).first()
        if not error:
            session.close()
            return jsonify({"error": "No persisted error"}), 404
        result = error.to_dict()
        session.close()
        return jsonify(result), 200
    except Exception:
        session.close()
        return jsonify({"error": "Failed to read persisted error"}), 500


@timetable_bp.route('/timetable', methods=['POST'])
def generate_timetable():
    """Start asynchronous timetable generation. Returns existing running task when present."""
    running_status = task_manager.get_current_status()
    if running_status:
        task_id = running_status.get("task_id")
        logger.info(
            "Timetable generation requested while another task is running",
            extra=build_log_extra(task_id=task_id),
        )
        return jsonify(running_status), 202

    _clear_scheduler_error()
    task_id = task_manager.create_task()
    locale = get_current_locale()
    logger.info("Timetable generation task created locale=%s", locale, extra=build_log_extra(task_id=task_id))
    thread = threading.Thread(
        target=_run_solver_in_background,
        args=(task_id, locale),
        daemon=True,
    )
    thread.start()
    logger.info("Timetable generation thread started", extra=build_log_extra(task_id=task_id))
    return jsonify(task_manager.get_status(task_id)), 202


@timetable_bp.route('/timetable/status/current', methods=['GET'])
def get_current_task_status():
    """Poll current active task, or latest known task if nothing is running."""
    status = task_manager.get_current_status() or task_manager.get_latest_status()
    if status is None:
        logger.debug("Current task status requested with no known tasks", extra=build_log_extra())
        return jsonify({"status": "idle", "task_id": None}), 200

    logger.debug(
        "Current task status requested status=%s",
        status.get("status"),
        extra=build_log_extra(task_id=status.get("task_id")),
    )
    return jsonify(status), 200


@timetable_bp.route('/timetable/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Poll task status. Returns running/success/error/cancelled."""
    status = task_manager.get_status(task_id)
    if status is None:
        logger.warning("Task status requested for unknown task", extra=build_log_extra(task_id=task_id))
        return jsonify({"error": "Task not found"}), 404
    logger.debug("Task status requested status=%s", status.get("status"), extra=build_log_extra(task_id=task_id))
    return jsonify(status), 200


@timetable_bp.route('/timetable/<task_id>/cancel', methods=['POST'])
def cancel_generation(task_id):
    """Mark a running generation task as cancelled."""
    task_manager.cancel_task(task_id)
    logger.info("Task cancellation requested", extra=build_log_extra(task_id=task_id))
    return jsonify({"status": "cancelled"}), 200


@timetable_bp.route('/timetable', methods=['DELETE'])
def clear_assignments():
    """Delete all timetable assignments and persisted error."""
    session = DbSession()
    logger.info("Clearing timetable assignments", extra=build_log_extra())
    session.query(TimeSlotAssignment).delete()
    session.commit()
    session.close()
    _clear_scheduler_error()
    logger.info("Timetable assignments and persisted error cleared", extra=build_log_extra())
    return jsonify({'status': 'ok', 'message': t('timetable.assignments_cleared')}), 200
