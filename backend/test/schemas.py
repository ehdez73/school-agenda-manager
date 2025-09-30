from pydantic import BaseModel
from typing import List, Optional


class TestSubject(BaseModel):
    id: str
    course_id: str
    weekly_hours: int = 0
    subjectgroup_id: Optional[str] = None
    __test__ = False


class TestSubjectGroup(BaseModel):
    id: str
    subject_ids: List[str]
    __test__ = False


class TestTeacher(BaseModel):
    id: str
    max_hours_week: int
    __test__ = False
