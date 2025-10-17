import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Table, ForeignKey, Column as SAColumn
from sqlalchemy import Boolean

ENGINE = create_engine("sqlite:///agenda.db")
Base = declarative_base()
Session = sessionmaker(bind=ENGINE)


class Course(Base):
    """
    Represents a school course.
    Attributes:
        id (str): Unique identifier for the course (e.g., "1º", "2º").
        num_lines (int): Number of lines/groups in the course (e.g., 2 for "1ºA", "1ºB").
    """

    __tablename__ = "courses"
    id = Column(String(50), primary_key=True)
    num_lines = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<Course(id='{self.id}', num_lines={self.num_lines})>"

    def to_dict(self):
        return {"id": self.id, "name": self.id, "num_lines": self.num_lines}


class Subject(Base):
    @property
    def full_name(self):
        if self.course:
            return f"{self.name} ({self.course.id})"
        elif self.course_id:
            return f"{self.name} ({self.course_id})"
        return self.name

    """
    Represents a school subject.
    Attributes:
        id (str): Unique identifier for the subject.
        name (str): Name of the subject.
        weekly_hours (int): Number of hours per week.
        max_hours_per_day (int): Maximum hours per day for the subject.
        course_id (str): Foreign key to Course.
        course (Course): Relationship to Course.
        groups (list[SubjectGroup]): Groups associated with the subject.
    """
    __tablename__ = "subjects"
    id = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)
    weekly_hours = Column(Integer, nullable=False, default=1)
    max_hours_per_day = Column(Integer, nullable=False, default=1)
    # If True, when a subject has more than one hour per day those hours must be consecutive.
    # If False, they must NOT be consecutive.
    consecutive_hours = Column(Boolean, nullable=False, default=True)
    # If True, the subject must be taught at least once every day of the configured week
    teach_every_day = Column(Boolean, nullable=False, default=False)
    # Optional link to another subject that should be scheduled consecutively when on same day
    linked_subject_id = Column(String(20), ForeignKey("subjects.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course", backref="subjects")

    def __repr__(self):
        return (
            f"<Subject(id='{self.id}', name='{self.name}', course_id={self.course_id})>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "weekly_hours": self.weekly_hours,
            "teach_every_day": self.teach_every_day,
            "max_hours_per_day": self.max_hours_per_day,
            "consecutive_hours": self.consecutive_hours,
            "course": self.course.to_dict() if self.course else None,
            "subject_groups": [
                {"id": g.id, "name": g.name} for g in self.subject_groups
            ]
            if getattr(self, "subject_groups", None)
            else [],
            "full_name": self.full_name,
            "linked_subject_id": getattr(self, "linked_subject_id", None),
        }


subjectgroup_subject = Table(
    "subjectgroup_subject",
    Base.metadata,
    Column("subjectgroup_id", Integer, ForeignKey("subject_groups.id")),
    Column("subject_id", String(20), ForeignKey("subjects.id")),
)


class SubjectGroup(Base):
    """
    Represents a group of subjects that can share a timeslot.
    Attributes:
        id (int): Primary key.
        name (str): Optional display name for the group.
        subjects (list[Subject]): Subjects belonging to the group.
    """

    __tablename__ = "subject_groups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)

    subjects = relationship(
        "Subject", secondary=subjectgroup_subject, backref="subject_groups"
    )

    def __repr__(self):
        return f"<SubjectGroup(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subjects": [s.to_dict() for s in self.subjects],
        }


teacher_subject = Table(
    "teacher_subject",
    Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.id")),
    Column("subject_id", Integer, ForeignKey("subjects.id")),
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

    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    subjects = relationship("Subject", secondary=teacher_subject, backref="teachers")
    max_hours_week = Column(Integer, nullable=False, default=1)

    preferences = Column(String(1000), nullable=True)
    # store the tutor group as a string like '1ºA' or null when no tutor assigned
    tutor_group = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subjects": [subject.to_dict() for subject in self.subjects],
            "max_hours_week": self.max_hours_week,
            "preferences": json.loads(self.preferences) if self.preferences else {},
            "tutor_group": self.tutor_group,
        }


class Timeslot(Base):
    """
    Represents a timeslot in the timetable.
    Attributes:
        id (int): Unique identifier for the timeslot.
        day (int): Day index of the week (0 = first weekday, e.g. Monday).
        hour (int): Hour of the day.
        course_id (str): Foreign key to Course.
        line (int): Line/group number (e.g., 1 = 1ºA, 2 = 1ºB).
        course (Course): Relationship to Course.
    """

    __tablename__ = "timeslots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    course_id = Column(String(50), ForeignKey("courses.id"), nullable=False)
    line = Column(
        Integer, nullable=False
    )  # e.g.: 1 = first line/group (A), 2 = second line/group (B)

    course = relationship("Course", backref="timeslots")
    timeslot_assignments = relationship("TimeSlotAssignment", back_populates="timeslot")
    subject_group_id = Column(Integer, ForeignKey("subject_groups.id"), nullable=True)
    subject_group = relationship("SubjectGroup", backref="timeslots")

    def __repr__(self):
        return f"<:Timeslot(id={self.id}, day={self.day}, hour={self.hour}, course={self.course_id}, line={self.line})>"


class TimeSlotAssignment(Base):
    """
    Represents a scheduled timeslot assignment (class session).
    Attributes:
        id (int): Unique identifier for the assignment.
        timeslot_id (int): Foreign key to Timeslot.
        subject_id (str): Foreign key to Subject.
        teacher_id (int): Foreign key to Teacher.
        timeslot (Timeslot): Relationship to Timeslot.
        subject (Subject): Relationship to Subject.
        teacher (Teacher): Relationship to Teacher.
    """

    __tablename__ = "timeslot_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timeslot_id = Column(Integer, ForeignKey("timeslots.id"))
    subject_id = Column(String(20), ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    timeslot = relationship("Timeslot", back_populates="timeslot_assignments")
    subject = relationship("Subject")
    teacher = relationship("Teacher")

    def __repr__(self):
        return f"<TimeSlotAssignment(id={self.id}, subject={self.subject_id}, teacher={self.teacher_id}, timeslot_id={self.timeslot_id})>"


class Config(Base):
    """
    Represents general configuration for the timetable system.
    Attributes:
        id (int): Unique identifier for the config.
        classes_per_day (int): Number of classes per day.
        days_per_week (int): Number of days per week.
    """

    __tablename__ = "config"
    id = Column(Integer, primary_key=True)
    classes_per_day = Column(Integer, nullable=False, default=5)
    days_per_week = Column(Integer, nullable=False, default=5)
    hour_names = Column(String(2000), nullable=True)
    day_indices = Column(String(2000), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "classes_per_day": self.classes_per_day,
            "days_per_week": self.days_per_week,
            "hour_names": json.loads(self.hour_names) if self.hour_names else [],
            "day_indices": json.loads(self.day_indices) if self.day_indices else [],
        }


Base.metadata.create_all(ENGINE)
