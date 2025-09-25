
# Script para poblar la base de datos usando los modelos de SQLAlchemy
from models import ENGINE, Session, Course, Subject, Teacher, Timeslot, Activity, Config
from sqlalchemy import inspect
from models import Base


def populate_db():
    inspector = inspect(ENGINE)
    
    if not inspector.has_table('teachers'):
        Base.metadata.create_all(ENGINE)
        print("tables created in agenda.db")

    
    session = Session()
    
    session.query(Course).delete()
    session.query(Subject).delete()
    session.query(Teacher).delete()
    session.query(Timeslot).delete()
    session.query(Activity).delete()
    session.query(Config).delete()
    
    
    # Config
    session.add(Config(classes_per_day=5))

    # Cursos: 1ºA, 1ºB, 2ºA, 2ºB, 3ºA, 3ºB
    courses = [
        Course(id="1º", num_lines=2),
        Course(id="2º", num_lines=2),
        Course(id="3º", num_lines=2),
    ]
    session.add_all(courses)

    # Materias para cada curso (ejemplo: mismas materias para todos)
    subjects = []
    subject_defs = [
        ("MAT", "Matemáticas", 5),
        ("LEN", "Lengua", 5),
        ("CIE", "Ciencias", 3),
        ("ING", "Inglés", 2),
        ("EFI", "Educación Física", 2),
    ]
    for course in courses:
        for sid, name, wh in subject_defs:
            subjects.append(Subject(id=f"{sid}_{course.id}", name=f"{name} {course.id}", weekly_hours=wh, course=course))
    session.add_all(subjects)

    # Profesores
    teachers = [
        Teacher(name="Ana Pérez", weekly_hours=20),
        Teacher(name="Luis Gómez", weekly_hours=20),
        Teacher(name="María López", weekly_hours=20),
    ]
    # Asignar materias a profesores (todas las líneas de cada materia)
    for subject in subjects:
        if "MAT" in subject.id:
            teachers[0].subjects.append(subject)
        elif "LEN" in subject.id:
            teachers[1].subjects.append(subject)
        elif "CIE" in subject.id:
            teachers[2].subjects.append(subject)
        elif "ING" in subject.id:
            teachers[0].subjects.append(subject)
        elif "EFI" in subject.id:
            teachers[1].subjects.append(subject)
    session.add_all(teachers)

    # Franjas horarias para cada curso y línea (lunes a viernes, 8-12h)
    timeslots = []
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    for course in courses:
        for line in range(1, 3):
            for day in days:
                for hour in range(8, 13):
                    timeslots.append(Timeslot(day=day, hour=hour, course_id=course.id, line=line))
    session.add_all(timeslots)

    # Actividades: asignar materias y profesores a las primeras franjas de cada curso/línea
    activities = []
    for i, course in enumerate(courses):
        # Para cada línea (1 y 2)
        for line in range(1, 3):
            # Buscar timeslots de este curso y línea
            ts = [t for t in timeslots if t.course_id == course.id and t.line == line]
            # Buscar materias de este curso
            subs = [s for s in subjects if s.course == course]
            # Asignar las primeras materias a las primeras franjas
            for j in range(min(len(subs), len(ts))):
                # Asignar profesor según materia
                if "MAT" in subs[j].id:
                    teacher = teachers[0]
                elif "LEN" in subs[j].id:
                    teacher = teachers[1]
                elif "CIE" in subs[j].id:
                    teacher = teachers[2]
                elif "ING" in subs[j].id:
                    teacher = teachers[0]
                elif "EFI" in subs[j].id:
                    teacher = teachers[1]
                activities.append(Activity(timeslot=ts[j], subject=subs[j], teacher=teacher))
    session.add_all(activities)

    session.commit()
    session.close()
    print("Base de datos rellenada con ejemplos válidos usando SQLAlchemy.")
