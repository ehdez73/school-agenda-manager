import logging
import time

from flask import Flask, request, g
from flask_cors import CORS

from .routes.courses import courses_bp
from .routes.subjects import subjects_bp
from .routes.teachers import teachers_bp
from .routes.subject_groups import subject_groups_bp
from .routes.fixed_slots import fixed_slots_bp
from .routes.export_import import export_import_bp

from .populate_db import populate_db
from .routes.timetable import timetable_bp
from .routes.config import config_bp
from .translations import set_locale
from .constants import DEFAULT_LOCALE
from .logging_config import setup_logging, build_log_extra, get_request_id

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Initializing backend database", extra=build_log_extra())
populate_db("backend/init-data.json")
logger.info("Backend database initialization complete", extra=build_log_extra())

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones desde el frontend


@app.before_request
def set_request_locale():
    """Set the locale for this request based on X-Locale header."""
    g.request_started_at = time.perf_counter()
    get_request_id()
    locale = request.headers.get("X-Locale") or DEFAULT_LOCALE
    set_locale(locale)
    logger.info(
        "Request started method=%s path=%s locale=%s",
        request.method,
        request.path,
        locale,
        extra=build_log_extra(),
    )


@app.after_request
def log_request_result(response):
    duration_ms = 0.0
    started_at = getattr(g, "request_started_at", None)
    if started_at is not None:
        duration_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "Request completed method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.path,
        response.status_code,
        duration_ms,
        extra=build_log_extra(),
    )
    return response


app.register_blueprint(courses_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(teachers_bp)
app.register_blueprint(subject_groups_bp)
app.register_blueprint(export_import_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(fixed_slots_bp)
app.register_blueprint(config_bp)
