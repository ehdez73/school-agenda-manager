"""Simple backend translation helper.

This is intentionally minimal: it provides a t(key, **vars) function and a small
dictionary with messages in Spanish and English. The app can import t and use
it for user-facing messages. For a full solution consider integrating Flask-Babel.
"""

from flask import g, has_request_context
from .constants import DEFAULT_LOCALE

_LOCALES = {
    "en": {
        "errors.missing_name": "Required data missing (name)",
        "errors.missing_required_data": "Required data missing (id, name)",
        "errors.hours_mismatch": "All selected subjects must have the same weekly hours",
        "errors.not_found": "{entity} with ID {id} not found",
        "errors.no_data_provided": "No data provided for update",
        "errors.missing_field": "Missing required field '{field}'",
        "errors.missing_classes_per_day": "classes_per_day and days_per_week are required",
        "errors.invalid_days_per_week": "days_per_week must be between 1 and 7",
        "errors.duplicate_days": "Each day must be unique. Please select different days for each position.",
        "errors.invalid_preferences": "preferences must be dict(day -> {{unavailable: [...], preferred: [...]}}) with integer lists",
        "errors.json_no_content": "No JSON content provided",
        "errors.json_parse_error": "JSON parse error: {error}",
        "errors.import_failed": "Import failed: {error}",
        "errors.clear_data_failed": "Clear data failed: {error}",
        "errors.timetable_generation_error": "Error generating timetable: {error}",
        "success.deleted": "{entity} with ID {id} deleted successfully",
        "success.import_completed": "Import completed",
        "success.data_cleared": "All data cleared successfully",
        "timetable.no_schedule": "No timetables generated. Please generate a timetable first.",
        "timetable.generate_failed": "Could not generate a valid timetable",
        "timetable.generated_success": "Timetable generated successfully",
        "timetable.assignments_cleared": "Assignments cleared",
        "timetable.by_course": "Timetables by course",
        "timetable.by_teacher": "Timetables by teacher",
        "timetable.teacher_hours": "({assigned}/{max} hours)",
        "hours.label": "Hour {n}",
        "timetable.course_label": "Course",
        "timetable.hour_header": "Hour",
        "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "day.0": "Monday",
        "day.1": "Tuesday",
        "day.2": "Wednesday",
        "day.3": "Thursday",
        "day.4": "Friday",
        "day.5": "Saturday",
        "day.6": "Sunday",
    },
    "es": {
        "errors.missing_name": "Faltan datos requeridos (name)",
        "errors.missing_required_data": "Faltan datos requeridos (id, name)",
        "errors.hours_mismatch": "Todas las asignaturas del grupo deben tener el mismo número de horas semanales",
        "errors.not_found": "{entity} con ID {id} no encontrado",
        "errors.no_data_provided": "No se proporcionaron datos para actualizar",
        "errors.missing_field": "Falta el campo '{field}'",
        "errors.invalid_max_hours": "max_hours_week debe ser un número positivo",
        "errors.invalid_days_per_week": "days_per_week debe estar entre 1 y 7",
        "errors.duplicate_days": "Cada día debe ser único. Por favor, selecciona días diferentes para cada posición.",
        "errors.missing_classes_per_day": "classes_per_day y days_per_week son requeridos",
        "errors.invalid_preferences": "preferences debe ser dict(día -> {{unavailable: [...], preferred: [...]}}) con listas de enteros",
        "errors.json_no_content": "No se proporcionó contenido JSON",
        "errors.json_parse_error": "Error de análisis JSON: {error}",
        "errors.import_failed": "Importación fallida: {error}",
        "errors.clear_data_failed": "Error al limpiar datos: {error}",
        "errors.timetable_generation_error": "Error al generar el horario: {error}",
        "success.deleted": "{entity} con ID {id} eliminado correctamente",
        "success.import_completed": "Importación completada",
        "success.data_cleared": "Todos los datos eliminados correctamente",
        "timetable.no_schedule": "No hay horarios generados. Por favor, genere un horario primero.",
        "timetable.generate_failed": "No se pudo generar un horario válido",
        "timetable.generated_success": "Horario generado exitosamente",
        "timetable.assignments_cleared": "Assignments eliminadas",
        "timetable.by_course": "Horarios por curso",
        "timetable.by_teacher": "Horarios por docente",
        "timetable.teacher_hours": "({assigned}/{max} horas)",
        "hours.label": "Hora {n}",
        "timetable.course_label": "Curso",
        "timetable.hour_header": "Hora",
        "weekdays": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
        "day.0": "Lunes",
        "day.1": "Martes",
        "day.2": "Miércoles",
        "day.3": "Jueves",
        "day.4": "Viernes",
        "day.5": "Sábado",
        "day.6": "Domingo",
    },
}

# default locale for backend responses
_DEFAULT_LOCALE = DEFAULT_LOCALE


def get_current_locale():
    """Get the current locale for this request."""
    if has_request_context():
        return getattr(g, "locale", _DEFAULT_LOCALE)
    return _DEFAULT_LOCALE


def set_locale(l):
    """Set the locale for the current request."""
    if l in _LOCALES:
        g.locale = l


def t(key, **vars):
    current_locale = get_current_locale()
    msg = _LOCALES.get(current_locale, _LOCALES["en"]).get(key)
    if msg is None:
        # fallback to english or key
        msg = _LOCALES["en"].get(key, key)
    if isinstance(msg, str):
        try:
            return msg.format(**vars)
        except Exception:
            return msg
    return msg
