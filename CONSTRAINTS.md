# Constraints

This document describes all the rules the timetable generator must follow when
creating schedules. It serves as the single source of truth for the scheduling
logic — both for developers implementing the solver and for stakeholders
reviewing what the system will and won't do.

Two categories exist:

- **Hard constraints** must always be satisfied. The generator will reject any
  solution that violates even one of these rules.
- **Soft constraints** are preferences that should be maximized where
  possible. The generator will try to satisfy as many as it can, but may leave
  some unmet if no feasible schedule exists.

# Schedule filling process

## Context

### Domain Model

The system follows these general rules:

- A school has several **grades**, e.g. 1st, 2nd, 3rd, etc.
- Each **grade** can have several **classes** (depending on the number of students), e.g. 1A, 1B, 1C, etc.
- Each **grade** has several **subjects**, e.g. Math 1st, Math 2nd, Language 1st, Science 3rd, etc.
- Each **subject** has a number of **weekly hours** depending on its workload, e.g. Math 1st 4 hours, Math 2nd 5 hours, Language 1st 5 hours, etc.
- Some **subjects** are grouped into **SubjectGroups** so they always share the same timeslot e.g.: Religion + Ethics values.
- There are several **teachers**, each can teach several **subjects**.
- Each **teacher** has a **maximum number of teaching hours** per week (between 1 and 40, default 20).
- A teacher can be restricted to specific **course lines** per subject via `teacher_subject_lines`. For example, a teacher may teach Language only to lines A and B of 6th grade, while another teacher covers line C. This filtering happens at the assignment-variable creation level, **before** any constraint is applied — the solver never considers invalid (teacher, line) combinations.
- Each day-period slot per teacher is one of: **None** (default), **Unavailable** (hard constraint — cannot teach that slot), or **Preferred** (soft constraint). A slot cannot be both unavailable and preferred — setting one clears the other.
- Each **day** has a **limited number of teaching hours** (between 1 and 8), defined by configuration, e.g. 5 hours/day

### Goals

- A weekly timetable must be generated, spanning Monday to Friday, covering all subjects and grades, taking into account the weekly hours of each subject and that a teacher cannot teach two classes at the same time.
- Timetables should distribute subjects evenly throughout the week, avoiding concentrating all hours of a subject on a single day.
- Timetables must be generated automatically.
- The final result should be a clear and easy-to-understand timetable, showing which subject is taught in each grade, on which day and at what time, as well as the teacher in charge of each class.
- Once the timetables are generated, a personalized timetable for each teacher will be created from the previous ones.

## Constraints

### Hard

- A teacher cannot teach two groups at the same time (joint classes count as a single logical unit — the teacher is considered to be teaching one class)
- Do not exceed the teacher's maximum weekly hours (joint classes count once per slot; coordination hours are subtracted from the available limit)
- Respect the teacher's mandatory availability schedules
- Cover all weekly hours for each subject
- Do not exceed maximum hours per day per subject (per group)
- At most one teacher per (group, subject, day, hour) slot
- Each (group, subject) pair must be taught by at most one teacher across all hours of the week — a subject in a group cannot be split among multiple teachers (except when line-level restrictions via `teacher_subject_lines` assign different teachers to different course lines, e.g. Teacher A covers 6ºA+6ºB, Teacher B covers 6ºC)
- Subjects with "teach every day" flag must be taught at least once per day
- Maximum one "logical unit" (Subject or SubjectGroup) per group per hour per day — avoid gaps or overassignment
- If a subject requires consecutive hours, all its hours in a day must be consecutive
- If a subject does not require consecutive hours, they cannot be adjacent
- Linked subjects must be in adjacent hours
- Subjects in a SubjectGroup are always taught together
- Respect system configuration: periods per day
- Joint classes: multiple lines from the same course share the same subject, teacher, and time slot (with optional partial sharing where only `shared_hours` hours per week are joint; the remaining hours are taught independently per line)

### Soft (objective function to maximize)

- Reward teachers' preferred hours
- Reward tutors teaching classes in their own group
- Reward tutors who teach both the first and last hour of the week of their group *(configurable weight, default 500)*
- Avoid unnecessary gaps in the schedule for teachers *(teacher gaps implemented)*
- Distribute the hours of each subject evenly (avoid concentrating them on a single day) *(not yet implemented)*

## Constraint System (OR-Tools CP-SAT)

The constraints above are implemented using Google OR-Tools CP-SAT solver,
which translates them into a constraint satisfaction problem and searches for a
feasible schedule.

### Implementation classes

| Constraint | Class | Type | File |
|---|---|---|---|
| Teacher cannot teach two groups at once | `TeacherOneClassAtATime` | Hard | `backend/restrictions/teacher_one_class_at_a_time.py` |
| Teacher maximum weekly hours | `TeacherMaxWeeklyHours` | Hard | `backend/restrictions/teacher_max_weekly_hours.py` |
| Teacher unavailable times | `TeacherUnavailableTimes` | Hard | `backend/restrictions/teacher_unavailable_times.py` |
| Cover all subject weekly hours | `SubjectWeeklyHours` | Hard | `backend/restrictions/subject_weekly_hours.py` |
| Max hours per day per subject (per group) | `GroupSubjectMaxHoursPerDay` | Hard | `backend/restrictions/group_subject_max_hours_per_day.py` |
| One teacher per slot per subject | `GroupSubjectAtMostOneTeacherPerTimeslot` | Hard | `backend/restrictions/group_subject_at_most_one_teacher_per_timeslot.py` |
| Teach-every-day flag | `SubjectMustEveryDay` | Hard | `backend/restrictions/subject_must_every_day.py` |
| One logical unit per slot | `GroupAtMostOneLogicalAssignment` | Hard | `backend/restrictions/group_at_most_one_logical_assignment.py` |
| Consecutive hours | `GroupSubjectHoursMustBeConsecutive` | Hard | `backend/restrictions/group_subject_hours_must_be_consecutive.py` |
| Non-consecutive hours | `GroupSubjectHoursMustNotBeConsecutive` | Hard | `backend/restrictions/group_subject_hours_must_not_be_consecutive.py` |
| Linked subjects adjacent | `LinkedSubjectsConsecutive` | Hard | `backend/restrictions/linked_subjects_consecutive.py` |
| SubjectGroup co-assignment | `SubjectGroupAssignment` | Hard | `backend/restrictions/subjectgroup_assignment.py` |
| Joint classes (multiple lines share slot + teacher) | `JointClassAssignment` | Hard | `backend/restrictions/joint_class_assignment.py` |
| One subject per group per teacher | `TeacherOneSubjectPerGroup` | Hard | `backend/restrictions/teacher_one_subject_per_group.py` |
| Teacher preferred times | `TeacherPreferredTimes` | Soft | `backend/restrictions/teacher_preferred_times.py` |
| Tutor teaches own group | `TutorPreference` | Soft | `backend/restrictions/tutor_preference.py` |
| Tutor first/last hour | `TutorMandatoryHours` | Soft | `backend/restrictions/tutor_mandatory_hours.py` |
| Avoid unnecessary gaps for teachers | `TeacherAvoidGaps` | Soft | `backend/restrictions/teacher_avoid_gaps.py` |

### Legacy / unused classes

The following restriction classes exist in the codebase but are **not connected to the solver**:

| Class | Reason | File |
|---|---|---|
| `GroupAtMostOneSubjectPerHour` | Superseded by `GroupAtMostOneLogicalAssignment` | `backend/restrictions/group_at_most_one_subject_per_hour.py` |
| `SubjectMaxHoursPerDay` | Superseded by `GroupSubjectMaxHoursPerDay` (per-group variant) | `backend/restrictions/subject_max_hours_per_day.py` |

Legacy standalone files (removed):
