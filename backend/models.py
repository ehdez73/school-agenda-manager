import json
from sqlalchemy import create_engine, Column, Integer, String, Text, UniqueConstraint, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Table, ForeignKey, Column as SAColumn
from sqlalchemy import Boolean

ENGINE = create_engine("sqlite:///agenda.db",
                       connect_args={"check_same_thread": False})
Base = declarative_base()
Session = sessionmaker(bind=ENGINE)


def normalize_tutor_groups(value):
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except Exception:
            return [text]
        value = parsed
    if isinstance(value, (list, tuple, set)):
        normalized = []
        seen = set()
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            normalized.append(text)
        return normalized
    text = str(value).strip()
    return [text] if text else []


def serialize_tutor_groups(value):
    groups = normalize_tutor_groups(value)
    return json.dumps(groups, ensure_ascii=False) if groups else None


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
    color = Column(String(7), nullable=False, default="#dbeafe")
    weekly_hours = Column(Integer, nullable=False, default=1)
    max_hours_per_day = Column(Integer, nullable=False, default=1)
    # If True, when a subject has more than one hour per day those hours must be consecutive.
    # If False, they must NOT be consecutive.
    consecutive_hours = Column(Boolean, nullable=False, default=True)
    # If True, they must NOT be consecutive.
    teach_every_day = Column(Boolean, nullable=False, default=False)
    # Optional link to another subject that should be scheduled consecutively when on same day
    linked_subject_id = Column(String(20), ForeignKey("subjects.id"), nullable=True)
    # JSON array of line indices to include (null = all lines), e.g. "[0, 1]" for lines A, B only
    included_lines = Column(Text, nullable=True)
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
            "color": self.color,
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
            "teachers": [{"id": t.id, "name": t.name} for t in self.teachers],
            "included_lines": json.loads(self.included_lines) if self.included_lines else None,
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
    color = Column(String(7), nullable=False, default="#fef3c7")
    # JSON array of line indices to include (null = all lines), e.g. "[0, 1]" for lines A, B only
    included_lines = Column(Text, nullable=True)
    # Number of hours that must be shared among all members. None = share all hours.
    shared_hours = Column(Integer, nullable=True)

    subjects = relationship(
        "Subject", secondary=subjectgroup_subject, backref="subject_groups"
    )

    def __repr__(self):
        return f"<SubjectGroup(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "subjects": [s.to_dict() for s in self.subjects],
            "included_lines": json.loads(self.included_lines) if self.included_lines else None,
            "shared_hours": self.shared_hours,
        }


teacher_subject = Table(
    "teacher_subject",
    Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teachers.id")),
    Column("subject_id", Integer, ForeignKey("subjects.id")),
    Column("included_lines", Text, nullable=True),
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
    coordination_hours = Column(Integer, nullable=False, default=0)

    preferences = Column(String(1000), nullable=True)
    # store tutor groups as a JSON array string or a legacy single group string
    tutor_group = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.name}')>"

    def get_tutor_groups(self):
        return normalize_tutor_groups(self.tutor_group)

    def set_tutor_groups(self, value):
        self.tutor_group = serialize_tutor_groups(value)

    def to_dict(self):
        tutor_groups = self.get_tutor_groups()
        return {
            "id": self.id,
            "name": self.name,
            "subjects": [subject.to_dict() for subject in self.subjects],
            "coordination_hours": self.coordination_hours,
            "max_hours_week": self.max_hours_week,
            "preferences": json.loads(self.preferences) if self.preferences else {},
            "tutor_group": tutor_groups[0] if tutor_groups else None,
            "tutor_groups": tutor_groups,
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


class FixedSlot(Base):
    """
    Represents a fixed/predefined row inserted into timetable display.
    These are visual-only entries that appear in the timetable at a given
    position, managed independently for courses vs teachers.
    Attributes:
        id (int): Primary key.
        slot_type (str): "course" or "teacher".
        position (int): 1-indexed position in the final timetable table.
        label (str): Display text, e.g., "Recreo", "Comedor".
        time_range (str): Time range display, e.g., "10:00-11:00".
    """

    __tablename__ = "fixed_slots"

    __table_args__ = (
        UniqueConstraint("slot_type", "position", name="uq_fixed_slots_type_position"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    slot_type = Column(String(20), nullable=False)
    position = Column(Integer, nullable=False)
    label = Column(String(200), nullable=False)
    time_range = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False, default="#f1f5f9")

    def __repr__(self):
        return (
            f"<FixedSlot(id={self.id}, type='{self.slot_type}', "
            f"pos={self.position}, label='{self.label}')>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "slot_type": self.slot_type,
            "position": self.position,
            "label": self.label,
            "time_range": self.time_range,
            "color": self.color,
        }


class TeacherFixedSlotLabel(Base):
    """
    Per-teacher per-day override for fixed slot labels.
    Allows each teacher to customise the text displayed in a specific
    day cell of a fixed slot row. When no entry exists the default
    FixedSlot label is used.
    """

    __tablename__ = "teacher_fixed_slot_labels"

    __table_args__ = (
        UniqueConstraint(
            "teacher_id", "fixed_slot_id", "day",
            name="uq_teacher_fixed_slot_day",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(
        Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    fixed_slot_id = Column(
        Integer, ForeignKey("fixed_slots.id", ondelete="CASCADE"), nullable=False
    )
    day = Column(Integer, nullable=False)
    label = Column(String(200), nullable=False, default="")

    teacher = relationship("Teacher", backref="fixed_slot_labels")
    fixed_slot = relationship("FixedSlot")


class CourseFixedSlotLabel(Base):
    """
    Per-course-line per-day override for fixed slot labels.
    Allows each course line to customise the text displayed in a specific
    day cell of a fixed slot row. When no entry exists the default
    FixedSlot label is used.
    """

    __tablename__ = "course_fixed_slot_labels"

    __table_args__ = (
        UniqueConstraint(
            "course_line", "fixed_slot_id", "day",
            name="uq_course_fixed_slot_day",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_line = Column(String(50), nullable=False, index=True)
    fixed_slot_id = Column(
        Integer, ForeignKey("fixed_slots.id", ondelete="CASCADE"), nullable=False
    )
    day = Column(Integer, nullable=False)
    label = Column(String(200), nullable=False, default="")

    fixed_slot = relationship("FixedSlot")


class TeacherBusySlot(Base):
    """
    Represents non-teaching time for a teacher (coordination, meetings, etc.).
    Persisted after the solver runs so coordination hours are stable across
    timetable renders and included in export/import.

    Attributes:
        id (int): Primary key.
        teacher_id (int): Foreign key to Teacher.
        day (int): Day index (0 = first weekday).
        hour (int): Hour index.
        slot_type (str): Type of busy slot (e.g. "coordinacion").
    """

    __tablename__ = "teacher_busy_slots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    slot_type = Column(String(50), nullable=False, default="coordinacion")

    teacher = relationship("Teacher", backref="busy_slots")


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
    day_colors = Column(Text, nullable=True)
    disabled_restrictions = Column(String(5000), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "classes_per_day": self.classes_per_day,
            "days_per_week": self.days_per_week,
            "hour_names": json.loads(self.hour_names) if self.hour_names else [],
            "day_indices": json.loads(self.day_indices) if self.day_indices else [],
            "day_colors": json.loads(self.day_colors) if self.day_colors else {},
            "disabled_restrictions": json.loads(self.disabled_restrictions) if self.disabled_restrictions else [],
        }


class SchedulerError(Base):
    """
    Persists the last scheduler failure diagnosis so it survives server restarts.
    Stores a single row (id=1) with the error message and full diagnosis markdown.
    """

    __tablename__ = "scheduler_errors"
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "message": self.message,
            "details": self.details,
            "created_at": self.created_at,
        }


class JointClass(Base):
    """
    Represents a joint class where multiple lines of a course share the same
    subject, teacher, and timeslot. For example, 6ºB and 6ºC both take Lengua
    together at the same time with the same teacher.

    Attributes:
        id (int): Primary key.
        name (str): Optional display name.
        course_id (str): Foreign key to Course.
        subject_id (str): Foreign key to Subject.
        teacher_id (int): Foreign key to Teacher (nullable — if None, the solver chooses).
        lines (str): JSON array of line letters, e.g. '["B", "C"]'.
        shared_hours (int): Number of shared hours. None = all hours are joint.
    """

    __tablename__ = "joint_classes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    course_id = Column(String(50), ForeignKey("courses.id"), nullable=False)
    subject_id = Column(String(20), ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    lines = Column(Text, nullable=False)
    shared_hours = Column(Integer, nullable=True)

    course = relationship("Course", backref="joint_classes")
    subject = relationship("Subject", backref="joint_classes")
    teacher = relationship("Teacher", backref="joint_classes")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "course_id": self.course_id,
            "subject_id": self.subject_id,
            "teacher_id": self.teacher_id,
            "lines": json.loads(self.lines) if self.lines else [],
            "shared_hours": self.shared_hours,
            "course": self.course.to_dict() if self.course else None,
            "subject": self.subject.to_dict() if self.subject else None,
            "teacher": self.teacher.to_dict() if self.teacher else None,
        }


class SupportAssignment(Base):
    """
    Represents a manual support assignment: a teacher assigned to support
    an existing subject in a course during one of their free slots.
    Created by the user after timetable generation.

    Attributes:
        id (int): Primary key.
        teacher_id (int): Foreign key to Teacher.
        day (int): Day index (0 = first weekday).
        hour (int): Hour index.
        subject_id (str): Foreign key to Subject being supported.
        course_id (str): Foreign key to Course where support is given.
        line (int): Line index of the course (0 = A, 1 = B, etc.).
    """

    __tablename__ = "support_assignments"
    __table_args__ = (
        UniqueConstraint(
            "course_id", "line", "day", "hour", "subject_id",
            name="uq_support_per_class",
        ),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    subject_id = Column(String(20), ForeignKey("subjects.id"), nullable=False)
    course_id = Column(String(50), ForeignKey("courses.id"), nullable=False)
    line = Column(Integer, nullable=False)

    teacher = relationship("Teacher", backref="support_assignments")
    subject = relationship("Subject")
    course = relationship("Course")


Base.metadata.create_all(ENGINE)

# Migration: add day_colors to existing config table if missing
try:
    inspector = inspect(ENGINE)
    existing_cols = [c["name"] for c in inspector.get_columns("config")]
    if "day_colors" not in existing_cols:
        with ENGINE.connect() as conn:
            conn.execute(text("ALTER TABLE config ADD COLUMN day_colors TEXT"))
            conn.commit()
except Exception:
    pass
