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

- **Courses**
- **Subjects** (includes a **Packs** tab for grouping subjects)
- **Teachers**
- **Timetable**
- **Configuration**
- **Help**

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

### Shared hours

Number of weekly hours where subjects in the Pack must coincide in the same timeslot.
- If no number is set (empty = "All hours"), **all hours** in the Pack are taught together.
- If a specific number is set, only those hours are shared; the remaining hours are independent per subject.

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

> **Recommendations:**
> - Check that all real lines in the school are created.
> - If a course has two groups, set 2 lines from the beginning.

### 5.2 Create subjects

1. Go to **Subjects**.
2. Create each subject with a name, course, color, and weekly hours.
3. If the course has multiple lines, you can **uncheck specific lines** to exclude the subject from those lines.
4. Complete optional fields when needed (max per day, consecutive hours, teach every day, linked subject, etc.).

> **Recommendations:**
> - Check that each subject has the correct weekly load.
> - Avoid duplicates with similar names.
> - If a subject is only taught in some lines, use the line checkboxes to exclude the ones it does not apply to.

### 5.3 Create Packs

1. Open the **Packs** tab inside Subjects.
2. Create the Pack with a clear name.
3. Select the subjects included in the Pack.
4. If needed, define shared hours.
5. Save.

> **Useful validations:**
> - Subjects in a Pack must be correctly defined first.
> - If you use shared hours, their value must be consistent with the weekly hours of the Pack subjects.

### 5.4 Create teachers

1. Go to Teachers.
2. Create each teacher with name.
3. Assign the subjects they can teach.
4. Set maximum weekly hours.
5. Assign tutor group(s) when applicable.

> **Recommendations:**
> - No subject should remain without assigned teachers.
> - Set realistic weekly maximums to avoid generation blocks.

#### 5.4.1 Configure availability and preferences

Each cell in the grid (day × hour) is a single button that cycles through three states on each click:

1. **No preference** (neutral/gray) — the teacher may or may not have class in that slot.
2. **Not available** (red) — the teacher cannot teach in that slot. The system will not assign classes here.
3. **Preferred** (green) — the teacher prefers to teach in that slot. The system will try to prioritize it.

Each click advances to the next state: `No preference → Not available → Preferred → No preference → ...`

> **Practical criterion:**
> - Use **Not available** only when mandatory (medical, duty, other school).
> - Use **Preferred** to guide the result without over-constraining it.
> - Changes are saved together with the rest of the teacher form.

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
5. Set shared hours = 1.
6. Save and verify.

Expected result:

- The Pack exists with shared hours = 1.
- The timetable enforces one shared weekly hour for that Pack.

### 6.3 Difference between a Pack without shared hours and a Pack with shared hours

- Pack **without** shared hours (empty = "All hours"): **all hours** of the Pack subjects are taught together in the same timeslot.
- Pack **with** shared hours (specific value): only that number of hours are taught together; the remaining hours are independent per subject.

## 7. Timetable generation and review

1. Go to **Timetable**.
2. Click **Generate Timetable**. The process may take a few seconds.
3. Wait for the process to finish.
4. The timetable appears in two sections: **by course** and **by teacher**.
   - Use the search filters and checkboxes at the top to choose which courses or teachers to display.
   - The sidebar provides quick navigation between groups or teachers.
   - Toggle **Show course/teacher fixed slots** to include or hide recess and other fixed blocks.
5. You can **Download Markdown** to save the timetable as a file, or **Print** for a paper-friendly view.
6. If needed, correct source data and generate again.

> **When to use Recreate Timetables:**
> - After major changes in courses, packs, or availability.
> - Recreate Timetables deletes the current timetable and generates a new one from scratch.

## 8. Constraints: HARD and SOFT

Go to **Configuration** and click the **Restrictions** tab. You will see two blocks:

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
| HARD | **SubjectWeeklyHours** | Ensures each subject meets its weekly hours per group. | Math 1st with 5h → appears exactly 5h. |
| HARD | **TeacherOneClassAtATime** | A teacher cannot teach two classes in the same timeslot. | English teacher cannot be in 2ndA and 2ndB at 10:00. |
| HARD | **TeacherUnavailableTimes** | Blocks timeslots marked as unavailable. | Tue 5th period unavailable → no class assigned there. |
| HARD | **TeacherMaxWeeklyHours** | Enforces each teacher's weekly max. | Max 23h → 24h cannot be assigned. |
| HARD | **GroupSubjectMaxHoursPerDay** | Limits how many times a subject can repeat in one day for a group. | Language max 2/day → cannot appear 3× on Tue in 3rdA. |
| HARD | **GroupAtMostOneLogicalAssignment** | A group can have only one subject (or Pack) per timeslot. | 1stA cannot have Math and Science at the same 3rd period. |
| HARD | **GroupSubjectAtMostOneTeacherPerTimeslot** | One subject+group cannot have two teachers in the same slot. | Music 4thA, 2nd period → one teacher only. |
| HARD | **GroupSubjectHoursMustBeConsecutive** | Subjects with "Consecutive hours": same-day hours form a contiguous block. | PE 5thA, 2h on Thu → must be 4th-5th, not 2nd and 5th. |
| HARD | **GroupSubjectHoursMustNotBeConsecutive** | Subjects WITHOUT "Consecutive hours": same-day hours cannot be adjacent. | Language 2ndB, 2h on Mon → cannot be 2nd-3rd. |
| HARD | **LinkedSubjectsConsecutive** | Linked subjects: when on the same day, they must be in contiguous hours. | Lab linked to Science → placed just before or after. |
| HARD | **SubjectGroupAssignment** | All Pack subjects are assigned to the same timeslot. | Religion and Educ. Support in RELAT1 → same slot. |
| HARD | **SubjectMustEveryDay** | Subjects marked "Teach every day": at least one hour daily. | Reading daily → appears Mon-Fri. |
| SOFT | **TutorMandatoryHours** | Rewards assigning the tutor to the first and last weekly periods of their group. | 1stA tutor preferred at start and end of week. |
| SOFT | **TeacherPreferredTimes** | Rewards placing classes in each teacher's preferred slots. | Teacher prefers morning → system tries to place classes there. |
| SOFT | **TutorPreference** | Rewards tutors teaching in their own tutor group. | 3rdB tutor → more hours in 3rdB than other groups. |
| SOFT | **TeacherAvoidGaps** | Penalizes gaps between classes, favoring compact daily blocks. | Better 2nd-3rd-4th consecutive than 2nd and 5th with gaps. |

## 9. Common issues and how to solve them

### Error 1: no valid timetable can be generated

Check:

- Subjects without assigned teacher.
- Teachers with weekly maximum too low.
- Too many unavailable timeslots.
- Misconfigured packs or inconsistent shared hours.

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
- Use shared hours only when there is a real pedagogical need.
- Avoid applying too many strict constraints to many teachers at once.
- Regenerate the timetable after each relevant block of changes.

## 11. Final checklist before generating

- [ ] General settings reviewed.
- [ ] Courses and lines completed.
- [ ] All subjects created with correct hours.
- [ ] Packs created and validated.
- [ ] Special cases configured:
  - [ ] Religion / Educational Support.
  - [ ] Communication and Representation of Reality / Music with shared hours=1 when applicable.
- [ ] All teachers assigned to subjects.
- [ ] Weekly maximums reviewed.
- [ ] Availabilities loaded correctly.
- [ ] Tutor assignments completed.

If the checklist is complete, generate the timetable.
