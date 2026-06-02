from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, RootModel


class CourseSchema(BaseModel):
    id: str
    name: str
    num_lines: int


class SubjectMinimalSchema(BaseModel):
    id: str
    name: str
    full_name: str
    course_id: Optional[str] = None


class SubjectSchema(BaseModel):
    id: str
    name: str
    color: str = "#dbeafe"
    weekly_hours: int
    max_hours_per_day: int
    consecutive_hours: bool = True
    teach_every_day: bool = False
    course: Optional[dict] = None
    subject_groups: List[dict] = []
    full_name: Optional[str] = None
    linked_subject_id: Optional[str] = None
    teachers: List[dict] = []
    included_lines: Optional[List[int]] = None


class SubjectGroupSchema(BaseModel):
    id: int
    name: Optional[str] = None
    color: str = "#fef3c7"
    subjects: List[SubjectMinimalSchema] = []
    included_lines: Optional[List[int]] = None
    shared_hours: Optional[int] = None


class DayPreferences(BaseModel):
    """Preferences for a single day.

    unavailable: list of integer hour indices that the teacher cannot teach that day
    preferred: list of integer hour indices that the teacher prefers that day
    """

    unavailable: List[int] = Field(default_factory=list)
    preferred: List[int] = Field(default_factory=list)


class PreferencesSchema(RootModel[Dict[Union[int, str], DayPreferences]]):
    """Root model mapping weekday index (int) or name (str) -> DayPreferences.

    The API uses weekday indices (0 = first day) for keys. For backwards
    compatibility this model also accepts weekday names as keys and the
    routes will normalize keys to indices before storing/returning.
    """

    root: Dict[Union[int, str], DayPreferences] = Field(default_factory=dict)


class TeacherSchema(BaseModel):
    id: int
    name: str
    subjects: List[SubjectMinimalSchema] = []
    coordination_hours: int = 0
    max_hours_week: int
    tutor_group: Optional[str] = None
    tutor_groups: List[str] = []
    # preferences is an optional mapping day->DayPreferences. We use PreferencesSchema
    # which accepts plain dicts and validates the inner shape.
    preferences: Optional[PreferencesSchema] = None


class FixedSlotCreate(BaseModel):
    slot_type: str = Field(..., pattern="^(course|teacher)$")
    position: int = Field(..., ge=1)
    label: str = Field(..., min_length=1)
    time_range: str = Field(..., min_length=1)


class FixedSlotUpdate(BaseModel):
    slot_type: Optional[str] = Field(None, pattern="^(course|teacher)$")
    position: Optional[int] = Field(None, ge=1)
    label: Optional[str] = Field(None, min_length=1)
    time_range: Optional[str] = Field(None, min_length=1)


class FixedSlotResponse(FixedSlotCreate):
    id: int


class JointClassSchema(BaseModel):
    id: int
    name: Optional[str] = None
    course_id: str
    subject_id: str
    teacher_id: Optional[int] = None
    lines: List[str] = []
    shared_hours: Optional[int] = None
    course: Optional[dict] = None
    subject: Optional[dict] = None
    teacher: Optional[dict] = None


class ConfigSchema(BaseModel):
    id: int
    classes_per_day: int
    days_per_week: int
    hour_names: List[str] = []
    day_indices: List[int] = []
    day_names: List[str] = []
    disabled_restrictions: List[str] = []
