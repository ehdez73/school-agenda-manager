"""Restrictions package - re-export individual restriction classes.

This package exposes a small API so callers may import restrictions like:

    from restrictions import SubjectGroupAssignment

Each restriction implementation lives in its own module inside this package.
"""
from .base import Restriction

from .group_subject_max_hours_per_day import GroupSubjectMaxHoursPerDay
from .group_at_most_one_logical_assignment import GroupAtMostOneLogicalAssignment
from .group_subject_hours_must_be_consecutive import GroupSubjectHoursMustBeConsecutive
from .subjectgroup_assignment import SubjectGroupAssignment
from .group_at_most_one_subject_per_hour import GroupAtMostOneSubjectPerHour

from .teacher_one_class_at_a_time import TeacherOneClassAtATime
from .teacher_max_weekly_hours import TeacherMaxWeeklyHours
from .teacher_unavailable_times import TeacherUnavailableTimes
from .teacher_preferred_times import TeacherPreferredTimes

from .subject_weekly_hours import SubjectWeeklyHours

__all__ = [
    "Restriction",
    "GroupSubjectMaxHoursPerDay",
    "GroupAtMostOneLogicalAssignment",
    "GroupSubjectHoursMustBeConsecutive",
    "SubjectGroupAssignment",
    "GroupAtMostOneSubjectPerHour",
    "TeacherOneClassAtATime",
    "TeacherMaxWeeklyHours",
    "TeacherUnavailableTimes",
    "TeacherPreferredTimes",
    "SubjectWeeklyHours",
]
