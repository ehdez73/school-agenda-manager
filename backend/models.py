# models.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Table, ForeignKey

ENGINE = create_engine('sqlite:///agenda.db')
Base = declarative_base()
Session = sessionmaker(bind=ENGINE)

class Course(Base):
    """
    Represents a school course.
    Attributes:
        id (str): Unique identifier for the course (e.g., "1º", "2º").
        num_lines (int): Number of lines/groups in the course (e.g., 2 for "1ºA", "1ºB").
   """
    __tablename__ = 'courses'
    id = Column(String(50), primary_key=True) 
    num_lines = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<Course(id='{self.id}', num_lines={self.num_lines})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.id,
            'num_lines': self.num_lines
        }

class Subject(Base):
    """
    Represents a school subject.
    Attributes:
        id (str): Unique identifier for the subject.
        name (str): Name of the subject.
        weekly_hours (int): Number of hours per week.
        course_id (str): Foreign key to Course.
        course (Course): Relationship to Course.
        groups (list[SubjectGroup]): Groups associated with the subject.
    """
    __tablename__ = 'subjects'
    id = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)
    weekly_hours = Column(Integer, nullable=False, default=1)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course", backref="subjects")

    # Relación con grupos
    groups = relationship(
        'SubjectGroup', secondary='subject_group_subject', back_populates='subjects'
    )

    def __repr__(self):
        return f"<Subject(id='{self.id}', name='{self.name}', course_id={self.course_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'weekly_hours': self.weekly_hours,
            'course': self.course.to_dict() if self.course else None
        }

class SubjectGroup(Base):
    """
    Represents a group of subjects (for grouping purposes).
    Attributes:
        id (int): Unique identifier for the group.
        name (str): Name of the group.
        subjects (list[Subject]): Subjects in the group.
    """
    __tablename__ = "subject_groups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    subjects = relationship(
        "Subject", secondary="subject_group_subject", back_populates="groups"
    )

    def __repr__(self):
        return f"<SubjectGroup(id={self.id}, name='{self.name}')>"


subject_group_subject = Table(
    "subject_group_subject",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("subject_groups.id")),
    Column("subject_id", String(20), ForeignKey("subjects.id")),
)


# Tabla de asociación muchos a muchos entre Teachers y Subjects
teacher_subject = Table(
    'teacher_subject', Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)


class Teacher(Base):
    """
    Represents a teacher.
    Attributes:
        id (int): Unique identifier for the teacher.
        name (str): Name of the teacher.
        subjects (list[Subject]): Subjects taught by the teacher.
        restrictions (str): Restrictions for scheduling.
        preferences (str): Preferences for scheduling.
        weekly_hours (int): Weekly teaching hours.
    """
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    subjects = relationship('Subject', secondary=teacher_subject, backref='teachers')
    restrictions = Column(String(255), nullable=True)
    preferences = Column(String(255), nullable=True)
    weekly_hours = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subjects': [subject.to_dict() for subject in self.subjects],
            'restrictions': self.restrictions,
            'preferences': self.preferences,
            'weekly_hours': self.weekly_hours
        }

class Timeslot(Base):
    """
    Represents a timeslot in the timetable.
    Attributes:
        id (int): Unique identifier for the timeslot.
        day (str): Day of the week.
        hour (int): Hour of the day.
        course_id (str): Foreign key to Course.
        line (int): Line/group number (e.g., 1 = 1ºA, 2 = 1ºB).
        course (Course): Relationship to Course.
        activities (list[Activity]): Activities scheduled in this timeslot.
    """
    __tablename__ = "timeslots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(String(20), nullable=False)
    hour = Column(Integer, nullable=False)
    course_id = Column(String(50), ForeignKey("courses.id"), nullable=False)
    line = Column(Integer, nullable=False)  # Ej: 1 = 1ºA, 2 = 1ºB

    course = relationship("Course", backref="timeslots")
    activities = relationship("Activity", back_populates="timeslot")

    def __repr__(self):
        return f"<Timeslot(id={self.id}, day={self.day}, hour={self.hour}, course={self.course_id}, line={self.line})>"


class Activity(Base):
    """
    Represents a scheduled activity (class session).
    Attributes:
        id (int): Unique identifier for the activity.
        timeslot_id (int): Foreign key to Timeslot.
        subject_id (str): Foreign key to Subject.
        teacher_id (int): Foreign key to Teacher.
        timeslot (Timeslot): Relationship to Timeslot.
        subject (Subject): Relationship to Subject.
        teacher (Teacher): Relationship to Teacher.
    """
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timeslot_id = Column(Integer, ForeignKey("timeslots.id"))
    subject_id = Column(String(20), ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    timeslot = relationship("Timeslot", back_populates="activities")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

    def __repr__(self):
        return f"<Activity(id={self.id}, subject={self.subject_id}, teacher={self.teacher_id}, classroom={self.classroom_id})>"

# Configuración general
class Config(Base):
    """
    Represents general configuration for the timetable system.
    Attributes:
        id (int): Unique identifier for the config.
        classes_per_day (int): Number of classes per day.
    """
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    classes_per_day = Column(Integer, nullable=False, default=5)

    def to_dict(self):
        return {
            'id': self.id,
            'classes_per_day': self.classes_per_day
        }

# Crea la tabla en la base de datos si no existe
Base.metadata.create_all(ENGINE)