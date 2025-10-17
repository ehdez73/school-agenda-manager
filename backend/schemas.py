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


class SubjectSchema(BaseModel):
    id: str
    name: str
    weekly_hours: int
    max_hours_per_day: int
    course: Optional[dict] = None
    subject_groups: List[dict] = []
    full_name: Optional[str] = None


class SubjectGroupSchema(BaseModel):
    id: int
    name: Optional[str] = None
    subjects: List[SubjectMinimalSchema] = []


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
    max_hours_week: int
    tutor_group: Optional[str] = None
    # preferences is an optional mapping day->DayPreferences. We use PreferencesSchema
    # which accepts plain dicts and validates the inner shape.
    preferences: Optional[PreferencesSchema] = None


class ConfigSchema(BaseModel):
    id: int
    classes_per_day: int
    days_per_week: int
    hour_names: List[str] = []
    day_indices: List[int] = []
    day_names: List[str] = []
