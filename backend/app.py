from flask import Flask, request
from flask_cors import CORS

from .routes.courses import courses_bp
from .routes.subjects import subjects_bp
from .routes.teachers import teachers_bp
from .routes.subject_groups import subject_groups_bp
from .routes.export_import import export_import_bp

from .populate_db import populate_db
from .routes.timetable import timetable_bp
from .routes.config import config_bp
from .translations import set_locale
from .constants import DEFAULT_LOCALE

populate_db("backend/init-data.json")

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones desde el frontend


@app.before_request
def set_request_locale():
    """Set the locale for this request based on X-Locale header."""
    locale = request.headers.get("X-Locale") or DEFAULT_LOCALE
    set_locale(locale)


app.register_blueprint(courses_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(teachers_bp)
app.register_blueprint(subject_groups_bp)
app.register_blueprint(export_import_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(config_bp)
