"""Simple backend translation helper.

This is intentionally minimal: it provides a t(key, **vars) function and a small
dictionary with messages in Spanish and English. The app can import t and use
it for user-facing messages. For a full solution consider integrating Flask-Babel.
"""

from flask import g, has_request_context
from .constants import DEFAULT_LOCALE

_LOCALES = {
    "en": {
        # --- Diagnosis / Solver messages ---
        "diagnosis.no_solution_title": "# ❌ No solution found — Diagnostic Results\n",
        "diagnosis.phase1_title": "## Phase 1 — Capacity sanity checks",
        "diagnosis.phase2_title": "## Phase 2 — Restriction isolation",
        "diagnosis.phase2_desc": "Removing any of these restrictions individually makes the model feasible:",
        "diagnosis.phase3_title": "## Phase 3 — Entity diagnosis",
        "diagnosis.phase3_timed_out": "  ⏱️ The diagnosis timed out. The constraints may be too complex for the allocated time. Try increasing timeout or simplifying.",
        "diagnosis.phase3_entities_title": "## Phase 3 — Specific entities involved",
        "diagnosis.entity_conflict": "- **{name}** — Conflicts involve:",
        "diagnosis.tutor_of_group": ", tutor of group {group}",
        "diagnosis.cleared_title": "Restrictions that did NOT cause issues individually:",
        "diagnosis.no_conclusion": "Could not isolate a single restriction. The infeasibility may arise from the interaction of multiple restrictions, or from data configuration.",
        "diagnosis.capacity_issue": "  - **Group {group}**: requires {required}h/week but only {available} slots available ({days} days × {hours} hours). Possible cause: **SubjectWeeklyHours**.",
        "diagnosis.subject_no_teacher": "  - **Subject \"{name}\" (id={id})** in **Group {group}** has no teacher assigned.",
        "diagnosis.subjectgroup_shared_hours_exceed": "  - **SubjectGroup \"{name}\"**: shared_hours={sh} exceeds min weekly_hours of members: {subjects}.",
        "diagnosis.subjectgroup_hours_mismatch": "  - **SubjectGroup \"{name}\"**: members have different weekly_hours: {subjects}. All subjects in a SubjectGroup must have the same weekly hours.",
        "diagnosis.teacher_capacity_issue": "  - **Teacher \"{name}\"** has max_hours_week={max} (effective={eff} with {coord}h coordination) but teaches \"{subj}\" requiring {subj_hours}h/week.",
        "diagnosis.global_capacity_issue": "  - **Global capacity**: total required hours ({required}h) exceed total teacher capacity ({capacity}h). Need more teachers or reduce subject hours.",
        "diagnosis.teach_every_day_hours": "  - **Subject \"{name}\"** has teach_every_day=True but only {hours}h/week (need at least {needed}h for {days} days).",
        "diagnosis.teach_every_day_max": "  - **Subject \"{name}\"** has teach_every_day=True, weekly_hours={wh}, but max possible with max_hours_per_day={mhpd} over {days} days is {max}h.",
        "diagnosis.infeasible_phase": "# ❌ No feasible solution found\n\nThe solver determined the model is infeasible. Starting diagnosis to identify the causes...\n",
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
        "errors.fixed_slot_position_occupied": "A fixed row of type '{slot_type}' already exists at position {position}.",
        "errors.timetable_generation_error": "Error generating timetable: {error}",
        "success.deleted": "{entity} with ID {id} deleted successfully",
        "success.import_completed": "Import completed",
        "success.data_cleared": "All data cleared successfully",
        "timetable.no_schedule": "No timetables generated. Please generate a timetable first.",
        "timetable.generate_failed": "Could not generate a valid timetable",
        "timetable.generated_success": "Timetable generated successfully",
        "timetable.assignments_cleared": "Assignments cleared",
        "timetable.by_course": "Courses",
        "timetable.by_teacher": "Teachers",
        "timetable.teacher_hours": "({assigned}/{max} hours)",
        "timetable.teacher_hours_coord": "({assigned}/{max} hours, {coord} coordination)",
        "timetable.coordination_label": "Coordination",
        "timetable.joint_class_label": "Joint",
        "hours.label": "Hour {n}",
        "timetable.course_label": "Course",
        "timetable.group_tutor": "Tutor",
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
        # --- Diagnosis / Solver messages ---
        "diagnosis.no_solution_title": "# ❌ No se encontró solución — Resultados del diagnóstico\n",
        "diagnosis.phase1_title": "## Fase 1 — Verificaciones de capacidad",
        "diagnosis.phase2_title": "## Fase 2 — Aislamiento de restricciones",
        "diagnosis.phase2_desc": "Eliminar cualquiera de estas restricciones individualmente hace factible el modelo:",
        "diagnosis.phase3_title": "## Fase 3 — Diagnóstico de entidades",
        "diagnosis.phase3_timed_out": "  ⏱️ El diagnóstico agotó el tiempo. Las restricciones pueden ser demasiado complejas para el tiempo asignado. Intenta aumentar el tiempo de espera o simplificar.",
        "diagnosis.phase3_entities_title": "## Fase 3 — Entidades específicas involucradas",
        "diagnosis.entity_conflict": "- **{name}** — Conflictos involucran:",
        "diagnosis.tutor_of_group": ", tutor del grupo {group}",
        "diagnosis.cleared_title": "Restricciones que NO causaron problemas individualmente:",
        "diagnosis.no_conclusion": "No se pudo aislar una restricción única. La inviabilidad puede deberse a la interacción de múltiples restricciones o a la configuración de datos.",
        "diagnosis.capacity_issue": "  - **Grupo {group}**: requiere {required}h/semana pero solo hay {available} espacios disponibles ({days} días × {hours} horas). Posible causa: **SubjectWeeklyHours**.",
        "diagnosis.subject_no_teacher": "  - **Asignatura \"{name}\" (id={id})** en **Grupo {group}** no tiene profesor asignado.",
        "diagnosis.subjectgroup_shared_hours_exceed": "  - **SubjectGroup \"{name}\"**: shared_hours={sh} excede el mínimo de horas semanales de los miembros: {subjects}.",
        "diagnosis.subjectgroup_hours_mismatch": "  - **SubjectGroup \"{name}\"**: los miembros tienen diferentes horas semanales: {subjects}. Todas las asignaturas en un SubjectGroup deben tener las mismas horas semanales.",
        "diagnosis.teacher_capacity_issue": "  - **Docente \"{name}\"** tiene max_hours_week={max} (efectivo={eff} con {coord}h de coordinación) pero enseña \"{subj}\" que requiere {subj_hours}h/semana.",
        "diagnosis.global_capacity_issue": "  - **Capacidad global**: las horas totales requeridas ({required}h) exceden la capacidad total de docentes ({capacity}h). Se necesitan más docentes o reducir horas de asignaturas.",
        "diagnosis.teach_every_day_hours": "  - **Asignatura \"{name}\"** tiene teach_every_day=True pero solo {hours}h/semana (necesita al menos {needed}h para {days} días).",
        "diagnosis.teach_every_day_max": "  - **Asignatura \"{name}\"** tiene teach_every_day=True, weekly_hours={wh}, pero el máximo posible con max_hours_per_day={mhpd} en {days} días es {max}h.",
        "diagnosis.infeasible_phase": "# ❌ No se encontró solución factible\n\nEl solver determinó que el modelo es inviable. Iniciando diagnóstico para identificar las causas...\n",
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
        "errors.fixed_slot_position_occupied": "Ya existe una fila fija de tipo '{slot_type}' en la posición {position}.",
        "errors.timetable_generation_error": "Error al generar el horario: {error}",
        "success.deleted": "{entity} con ID {id} eliminado correctamente",
        "success.import_completed": "Importación completada",
        "success.data_cleared": "Todos los datos eliminados correctamente",
        "timetable.no_schedule": "No hay horarios generados. Por favor, genere un horario primero.",
        "timetable.generate_failed": "No se pudo generar un horario válido",
        "timetable.generated_success": "Horario generado exitosamente",
        "timetable.assignments_cleared": "Assignments eliminadas",
        "timetable.by_course": "Cursos",
        "timetable.by_teacher": "Docentes",
        "timetable.teacher_hours": "({assigned}/{max} horas)",
        "timetable.teacher_hours_coord": "({assigned}/{max} horas, {coord} coordinación)",
        "timetable.coordination_label": "Coordinación",
        "timetable.joint_class_label": "Conjunta",
        "hours.label": "Hora {n}",
        "timetable.course_label": "Curso",
        "timetable.group_tutor": "Tutoría",
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
    return _translate(current_locale, key, **vars)


def t_locale(locale, key, **vars):
    """Translate using a specific locale (bypasses request context).

    Use this in background threads where Flask ``g`` is not available.
    """
    return _translate(locale, key, **vars)


def _translate(locale, key, **vars):
    msg = _LOCALES.get(locale, _LOCALES["en"]).get(key)
    if msg is None:
        # fallback to english or key
        msg = _LOCALES["en"].get(key, key)
    if isinstance(msg, str):
        try:
            return msg.format(**vars)
        except Exception:
            return msg
    return msg
