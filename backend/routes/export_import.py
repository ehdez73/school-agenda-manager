from flask import Blueprint, request, jsonify, Response, abort
from sqlalchemy.orm import joinedload
import json
from ..populate_db import init_config
from ..translations import t
from ..models import (
    Session,
    teacher_subject,
    subjectgroup_subject,
    Base,
    ENGINE,
    TimeSlotAssignment,
    Timeslot,
    Teacher,
    SubjectGroup,
    Subject,
    Course,
    Config,
)
from .. import export_import as shared_export_import

export_import_bp = Blueprint("export_import", __name__)


@export_import_bp.route("/api/export", methods=["GET"])
def export_json():
    session = Session()
    try:
        data = shared_export_import.dump_db(session)
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Disposition": "attachment; filename=agenda_export.json",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        # Return explicit 200 to avoid 304 responses from intermediate caches
        return Response(json_str, headers=headers, status=200)
    finally:
        session.close()


@export_import_bp.route("/api/import", methods=["POST"])
def import_json():
    # Try JSON from request body first, then file upload
    try:
        if request.files and "file" in request.files:
            content = request.files["file"].read().decode("utf-8")
            payload = json.loads(content)
        else:
            payload = request.get_json()
            if not payload:
                content = request.get_data(as_text=True)
                if content:
                    payload = json.loads(content)
                else:
                    abort(400, description=t("errors.json_no_content"))
    except Exception as e:
        abort(400, description=t("errors.json_parse_error", error=str(e)))

    # Recreate schema (drop and create) to ensure clean import
    try:
        # Recreate schema (drop and create) to ensure clean import
        try:
            Base.metadata.drop_all(ENGINE)
            Base.metadata.create_all(ENGINE)
        except Exception:
            # Fall through; we'll still try to insert
            pass

        session = Session()
        try:
            shared_export_import.import_payload(session, payload)
            session.commit()
            return jsonify(
                {"status": "ok", "message": t("success.import_completed")}
            ), 200
        except Exception as e:
            session.rollback()
            abort(500, description=t("errors.import_failed", error=str(e)))
        finally:
            session.close()
    except Exception as e:
        abort(500, description=t("errors.import_failed", error=str(e)))


@export_import_bp.route("/api/clear-all", methods=["DELETE"])
def clear_all_data():
    """Clear all data from all tables"""
    session = Session()
    try:
        # Delete all records from all tables in the correct order (to avoid foreign key constraints)
        session.query(TimeSlotAssignment).delete()
        session.query(Timeslot).delete()

        # Clear many-to-many relationships
        session.execute(teacher_subject.delete())
        session.execute(subjectgroup_subject.delete())

        # Delete main entities
        session.query(Teacher).delete()
        session.query(SubjectGroup).delete()
        session.query(Subject).delete()
        session.query(Course).delete()
        session.query(Config).delete()

        init_config(session)

        session.commit()
        return jsonify({"status": "ok", "message": t("success.data_cleared")}), 200
    except Exception as e:
        session.rollback()
        print(e)
        abort(500, description=t("errors.clear_data_failed", error=str(e)))
    finally:
        session.close()
