from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import Subject, Teacher, Course, Config, Session, ENGINE
from sqlalchemy.orm import joinedload
from routes.courses import courses_bp
from routes.subjects import subjects_bp
from routes.teachers import teachers_bp
from sqlalchemy import inspect
from models import Base

from populate_db import populate_db


populate_db()

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir peticiones desde el frontend
app.register_blueprint(courses_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(teachers_bp)


# --- Configuración general ---
@app.route('/config', methods=['GET'])
def get_config():
    session = Session()
    config = session.query(Config).first()
    if not config:
        # Si no existe, crea una config por defecto
        config = Config(classes_per_day=5)
        session.add(config)
        session.commit()
    result = config.to_dict()
    session.close()
    return jsonify(result)

@app.route('/config', methods=['POST'])
def set_config():
    data = request.get_json()
    if not data or 'classes_per_day' not in data:
        abort(400, description="Missing required field 'classes_per_day'")
    session = Session()
    config = session.query(Config).first()
    if not config:
        config = Config(classes_per_day=data['classes_per_day'])
        session.add(config)
    else:
        config.classes_per_day = data['classes_per_day']
    session.commit()
    result = config.to_dict()
    session.close()
    return jsonify(result)