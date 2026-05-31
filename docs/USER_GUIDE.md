# User Guide - School Agenda Manager

Guide aimed at Heads of Studies to manage the application: create the academic structure, configure teaching staff, and generate timetables.

This is a functional, day-to-day guide. It does not include technical aspects.

## Index

Note: this index is intended for quick navigation in your Markdown viewer side panel.

- [1. Application purpose](#1-application-purpose)
- [2. Quick section map](#2-quick-section-map)
- [3. Key definitions](#3-key-definitions)
- [4. Recommended workflow](#4-recommended-workflow)
- [5. How to create each element](#5-how-to-create-each-element)
- [6. Pack use cases](#6-pack-use-cases)
- [7. Timetable generation and review](#7-timetable-generation-and-review)
- [8. Constraints: HARD and SOFT](#8-constraints-hard-and-soft)
- [9. Common issues and how to solve them](#9-common-issues-and-how-to-solve-them)
- [10. Management best practices](#10-management-best-practices)
- [11. Final checklist before generating](#11-final-checklist-before-generating)

## 1. Application purpose

The application allows you to build and maintain school timetables in a centralized way, while respecting:

- The weekly load of each subject.
- Teacher availability and limits.
- Consistency by course and line.
- Pack rules and scheduling preferences.

## 2. Quick section map

In the top menu, day-to-day management is organized into:

- Courses
- Subjects
- Packs
- Teachers
- Timetables
- Settings

## 3. Key definitions

### Course

Educational level (for example, 1st, 2nd, I3, I4, I5).

### Line or Class

Subdivision of a course (A, B, etc.).
Example: 1stA and 1stB are two lines within course 1st.

### Subject

A subject taught in a course with a defined weekly load.
Example: Language 1st, Mathematics 3rd, Music I4A.

### Pack

A set of subjects managed in a coordinated way in the timetable.
In this guide, Pack is equivalent to Subject Group.

### shared_hours (shared hours within a Pack)

Number of weekly hours where subjects in the Pack must coincide in the same timeslot.

### Teacher

A teacher who teaches one or more subjects, with a maximum weekly load.

### Tutor

A teacher assigned to one or more tutor groups.

### Availability

Timeslots where the teacher cannot teach.

### Preferences

Preferred timeslots used to prioritize placement when generating the timetable.

## 4. Recommended workflow

To avoid errors and rework, always follow this order:

1. General settings (days, hours per day, time ranges).
2. Courses (and number of lines).
3. Subjects.
4. Packs.
5. Teachers.
6. Tutor assignment, availability, and preferences.
7. Timetable generation.
8. Review and adjustments.

## 5. How to create each element

### 5.1 Create courses

1. Go to Courses.
2. Create each course with its name.
3. Define the number of lines (A, B, etc.).

Recommendations:

- Check that all real lines in the school are created.
- If a course has two groups, set 2 lines from the beginning.

### 5.2 Create subjects

1. Go to Subjects.
2. Create each subject by setting course and weekly hours.
3. Complete optional fields when needed (max per day, teach every day, consecutive hours, etc.).

Recommendations:

- Check that each subject has the correct weekly load.
- Avoid duplicates with similar names.

### 5.3 Create Packs

1. Open the Packs tab inside Subjects.
2. Create the Pack with a clear name.
3. Select the subjects included in the Pack.
4. If needed, define shared_hours.
5. Save.

Useful validations:

- Subjects in a Pack must be correctly defined first.
- If you use shared_hours, its value must be consistent with the weekly hours of the Pack subjects.

### 5.4 Create teachers

1. Go to Teachers.
2. Create each teacher with name.
3. Assign the subjects they can teach.
4. Set maximum weekly hours.
5. Assign tutor group(s) when applicable.

Recommendations:

- No subject should remain without assigned teachers.
- Set realistic weekly maximums to avoid generation blocks.

### 5.5 Configure availability and preferences

1. Open a teacher profile.
2. Mark unavailable timeslots.
3. Mark preferred timeslots.
4. Save.

Practical criterion:

- Use unavailable slots only when mandatory.
- Use preferences to guide the result without over-constraining it.

## 6. Pack use cases

### 6.1 Religion / Educational Support case

Goal: manage both options as one coordinated block.

How to configure:

1. Create Religion subject for the corresponding course.
2. Create Educational Support subject for the same course.
3. Create a Pack (for example, RELAT1 for 1st).
4. Include both subjects in that Pack.
5. Save and verify that the Pack appears linked to both.

Expected result:

- The timetable treats this combination as a Pack.
- Timeslot consistency is preserved for this case.

### 6.2 Communication and Representation of Reality / Music case

Goal: model the specific Early Years case with shared hours.

How to configure:

1. Create Communication and Representation of Reality for the corresponding level.
2. Create Music for the same level.
3. Create one Pack per group/level (example: COMUI3A, COMUI4A, COMUI5A).
4. Add both subjects to the Pack.
5. Set shared_hours = 1.
6. Save and verify.

Expected result:

- The Pack exists with shared_hours = 1.
- The timetable enforces one shared weekly hour for that Pack.

### 6.3 Difference between a Pack without shared_hours and a Pack with shared_hours

- Pack without shared_hours: links subjects in the Pack without forcing an explicit number of shared hours.
- Pack with shared_hours: enforces exactly the number of shared hours indicated.

## 7. Timetable generation and review

1. Go to Timetables.
2. Click Generate Timetable.
3. Wait for the process to finish.
4. Review by course and by teacher.
5. If needed, correct data and generate again.

When to use Recreate Timetables:

- After major changes in courses, packs, or availability.

## 8. Constraints: HARD and SOFT

In Settings > Constraints you will see two blocks:

- Mandatory constraints (HARD).
- Optional preference constraints (SOFT).

### Difference between HARD and SOFT

- HARD: define conditions the timetable must satisfy to be valid. If they cannot be satisfied, a valid timetable is usually not generated.
- SOFT: do not invalidate the timetable if they are not fully satisfied. They are used to improve timetable quality (fewer gaps, better preference fit, etc.).

Quick example:

- HARD: A teacher cannot be in two classes at the same time.
- SOFT: Try to place a teacher in their preferred timeslots.

### Constraints table

| Type | Constraint | What it is for | Example |
| --- | --- | --- | --- |
| HARD | Subject weekly hours (SubjectWeeklyHours) | Ensures each subject meets its weekly hours for each group. | Mathematics 1st with 5 hours must appear exactly 5 hours. |
| HARD | One class at a time per teacher (TeacherOneClassAtATime) | Prevents a teacher from teaching two classes in the same timeslot. | The English teacher cannot be in 2ndA and 2ndB at 10:00 at the same time. |
| HARD | Teacher unavailable times (TeacherUnavailableTimes) | Blocks timeslots marked as unavailable. | If a teacher is unavailable on Tuesday 5th period, no class will be assigned there. |
| HARD | Teacher max weekly hours (TeacherMaxWeeklyHours) | Enforces each teacher's configured weekly maximum. | With a max of 23 hours, 24 or more cannot be assigned. |
| HARD | Subject max hours/day by group (GroupSubjectMaxHoursPerDay) | Limits how many times a subject can appear in one day for a group. | If Language has max 2 per day, it cannot appear 3 times on Tuesday in 3rdA. |
| HARD | One logical assignment per hour and group (GroupAtMostOneLogicalAssignment) | Ensures a group has only one subject (or Pack) per timeslot. | 1stA cannot have Mathematics and Science simultaneously in the 3rd period. |
| HARD | One teacher per subject in each timeslot (GroupSubjectAtMostOneTeacherPerTimeslot) | Prevents assigning two teachers to the same subject and group in the same timeslot. | Music in 4thA during the 2nd period cannot have two teachers at once. |
| HARD | Consecutive subject hours by group (GroupSubjectHoursMustBeConsecutive) | If a subject marked as consecutive appears multiple times in one day, those hours must form one continuous block. | If PE in 5thA has 2 hours on Thursday, they must be 4th-5th, not 2nd and 5th. |
| HARD | Non-consecutive subject hours by group (GroupSubjectHoursMustNotBeConsecutive) | For subjects marked as non-consecutive, separates same-day hours. | Language in 2ndB with 2 hours on Monday cannot be 2nd-3rd consecutively. |
| HARD | Linked subjects consecutive (LinkedSubjectsConsecutive) | When two subjects are linked, they must be in contiguous periods when they occur on the same day. | A lab linked to Science must be placed immediately before or after it. |
| HARD | Subject pack assignment (SubjectGroupAssignment) | Forces all Pack subjects to be assigned in the same timeslot. | Religion and Educational Support inside RELAT1 must share the Pack timeslot. |
| HARD | Subject must be taught every day (SubjectMustEveryDay) | For subjects marked with this option, requires at least one daily hour. | If a reading subject is marked daily, it must appear Monday to Friday. |
| SOFT | Tutor mandatory hours (TutorMandatoryHours) | Favors assigning the tutor in first and last weekly periods for their group. | Prioritizes the 1stA tutor teaching 1stA at the beginning and end of the week. |
| SOFT | Teacher preferred times (TeacherPreferredTimes) | Prioritizes placing classes in each teacher's preferred timeslots. | If a teacher prefers early morning, the system tries to place classes there. |
| SOFT | Tutor preference (TutorPreference) | Favors tutors teaching in their own tutor group. | Prioritizes the 3rdB tutor teaching more hours in 3rdB than in other groups. |
| SOFT | Avoid teacher gaps (TeacherAvoidGaps) | Penalizes timetables with gaps between classes, favoring compact blocks. | Better 2nd-3rd-4th consecutive than 2nd and 5th with gaps in between. |

## 9. Common issues and how to solve them

### Error 1: no valid timetable can be generated

Check:

- Subjects without assigned teacher.
- Teachers with weekly maximum too low.
- Too many unavailable timeslots.
- Misconfigured packs or inconsistent shared_hours.

### Error 2: a subject does not appear with expected hours

Check:

- Subject weekly hours.
- Whether it belongs to a Pack with constrained hours.
- Whether it is limited by max per day or consecutive/non-consecutive rules.

### Error 3: teacher overload

Check:

- Teacher weekly maximum.
- Subject distribution across more teachers.
- Overly restrictive availability.

### Error 4: tutor group conflict

Check:

- Tutor assignments in Teachers.
- That the same teacher is not overloaded with incompatible tutor group responsibilities.

## 10. Management best practices

- Keep naming consistent for courses, subjects, and packs.
- Create academic structure first, then teaching staff.
- Use shared_hours only when there is a real pedagogical need.
- Avoid applying too many strict constraints to many teachers at once.
- Regenerate the timetable after each relevant block of changes.

## 11. Final checklist before generating

- General settings reviewed.
- Courses and lines completed.
- All subjects created with correct hours.
- Packs created and validated.
- Special cases configured:
  - Religion / Educational Support.
  - Communication and Representation of Reality / Music with shared_hours=1 when applicable.
- All teachers assigned to subjects.
- Weekly maximums reviewed.
- Availabilities loaded correctly.
- Tutor assignments completed.

If the checklist is complete, generate the timetable.
