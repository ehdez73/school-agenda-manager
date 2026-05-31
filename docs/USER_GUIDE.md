# User Guide

Guide aimed at Heads of Studies to manage the application: create the academic structure, configure teaching staff, and generate timetables.

This is a functional, day-to-day guide. It does not include technical aspects.

## Index

Note: this index is intended for quick navigation in your Markdown viewer side panel.

- [1. Application purpose](#1-application-purpose)
- [2. Quick section map](#2-quick-section-map)
- [3. Key definitions](#3-key-definitions)
- [4. Configuration screen](#4-configuration-screen)
- [5. Recommended workflow](#5-recommended-workflow)
- [6. How to create each element](#6-how-to-create-each-element)
- [7. Pack use cases](#7-pack-use-cases)
- [8. Timetable generation and review](#8-timetable-generation-and-review)
- [9. How the generation process works](#9-how-the-generation-process-works)
- [10. Constraints: HARD and SOFT](#10-constraints-hard-and-soft)
- [11. Common issues and how to solve them](#11-common-issues-and-how-to-solve-them)
- [12. Management best practices](#12-management-best-practices)
- [13. Final checklist before generating](#13-final-checklist-before-generating)

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

### Availability grid

Grid where the teacher's unavailable and preferred timeslots are configured for timetable generation.

### Preferences

Preferred timeslots used to prioritize placement when generating the timetable.

## 4. Configuration screen

The **Configuration** screen (top menu) is organized into three tabs.

### 4.1 Schedules tab

Defines the school's time structure:

- **Days per week** (1-7): number of school days.
- **Day assignment**: which weekday (Monday to Sunday) corresponds to each position in the timetable.
- **Classes per day**: number of time slots per school day.
- **Hour names**: custom labels for each slot (e.g. "8:30-9:30", "Recess", ...).
- **Fixed slots**: recurring weekly blocks (e.g. recess, duty). They appear in the timetable but do not participate in class assignment.

Always save changes with the **Save** button.

### 4.2 Restrictions tab

Allows enabling or disabling individual restrictions. See [section 10](#10-constraints-hard-and-soft) for a detailed definition of each one.

- **Hard constraints**: conditions the timetable must satisfy to be valid. Disabling one may make generation easier, but the result could be pedagogically invalid.
- **Soft constraints**: preferences that improve timetable quality but do not block generation if unfulfilled.

All restrictions are enabled by default. Uncheck a box to disable it.

### 4.3 Backup tab

Manages all application data (courses, subjects, packs, teachers, timetables):

- **Export**: downloads an `agenda_export.json` file with all data.
- **Import**: select a previously exported JSON file to restore data.
- **Clear all data**: deletes all application data. Requires confirmation.

> **Recommendation:** export data before making major structural changes.

## 5. Recommended workflow

To avoid errors and rework, always follow this order:

1. General settings (days, hours per day, time ranges).
2. Courses (and number of lines).
3. Subjects.
4. Packs.
5. Teachers.
6. Tutor assignment, availability, and preferences.
7. Timetable generation.
8. Review and adjustments.

## 6. How to create each element

### 6.1 Create courses

1. Go to Courses.
2. Create each course with its name.
3. Define the number of lines (A, B, etc.).

> **Recommendations:**
> - Check that all real lines in the school are created.
> - If a course has two groups, set 2 lines from the beginning.

### 6.2 Create subjects

1. Go to **Subjects**.
2. Create each subject with a name, course, color, and weekly hours.
3. If the course has multiple lines, you can **uncheck specific lines** to exclude the subject from those lines.
4. Complete optional fields when needed (max per day, consecutive hours, teach every day, linked subject, etc.).

> **Recommendations:**
> - Check that each subject has the correct weekly load.
> - Avoid duplicates with similar names.
> - If a subject is only taught in some lines, use the line checkboxes to exclude the ones it does not apply to.

### 6.3 Create Packs

1. Open the **Packs** tab inside Subjects.
2. Create the Pack with a clear name.
3. Select the subjects included in the Pack.
4. If needed, define shared hours.
5. Save.

> **Useful validations:**
> - Subjects in a Pack must be correctly defined first.
> - If you use shared hours, their value must be consistent with the weekly hours of the Pack subjects.

### 6.4 Create teachers

1. Go to Teachers.
2. Create each teacher with name.
3. Assign the subjects they can teach.
4. Set maximum weekly hours.
5. Assign tutor group(s) when applicable.
6. Configure the availability grid (below).
7. If the teacher is a coordinator, assign the hours they will use for coordination.

> **Recommendations:**
> - No subject should remain without assigned teachers.
> - Set realistic weekly maximums to avoid generation blocks.

#### 6.4.1 Configure availability and preferences

Each cell in the grid (day × hour) is a single button that cycles through three states on each click:

1. **No preference** (neutral/gray) — the teacher may or may not have class in that slot.
2. **Not available** (red) — the teacher cannot teach in that slot. The system will not assign classes here.
3. **Preferred** (green) — the teacher prefers to teach in that slot. The system will try to prioritize it.

Each click advances to the next state: `No preference → Not available → Preferred → No preference → ...`

> **Practical criterion:**
> - Use **Not available** only when mandatory (medical, duty, other school).
> - Use **Preferred** to guide the result without over-constraining it.
> - Changes are saved together with the rest of the teacher form.

## 7. Pack use cases

### 7.1 Religion / Educational Support case

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

### 7.2 Communication and Representation of Reality / Music case

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

### 7.3 Difference between a Pack without shared hours and a Pack with shared hours

- Pack **without** shared hours (empty = "All hours"): **all hours** of the Pack subjects are taught together in the same timeslot.
- Pack **with** shared hours (specific value): only that number of hours are taught together; the remaining hours are independent per subject.

## 8. Timetable generation and review

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

## 9. How the generation process works

### 9.1 Generating a timetable

When you click **Generate Timetable**, the system uses Google OR-Tools, an optimization engine, to search for a valid combination of class assignments that satisfies all configured constraints.

### 9.2 Phases of the process

The generation goes through up to two phases:

**Phase 1 — Search for a solution**  
The solver attempts to find a valid timetable that meets all HARD constraints. If it succeeds, the timetable is displayed immediately.

**Phase 2 — Infeasibility diagnosis (only if Phase 1 fails)**  
If the solver cannot find a valid solution, it automatically starts a multi-step diagnostic process:

1. **Sanity checks** — Quick validation of the data model (e.g., every subject has a teacher, total hours are consistent).
2. **Isolation tests** — The system temporarily removes restrictions one by one to identify which constraint causes the conflict.
3. **Entity-level analysis** — For each conflictive constraint, it identifies the specific courses, teachers, or subjects involved.

The result is a diagnostic report describing exactly what prevents the timetable from being generated and what changes are recommended.

### 9.3 Why can it take so long?

Timetable generation is a **combinatorial explosion** problem. Consider a small school:

- 6 courses × 2 lines = 12 groups
- 10 subjects per group
- 5 days × 6 hours = 30 timeslots per week
- 15 teachers

Each class (group + subject) must be placed in one of the available timeslots, while respecting all constraints simultaneously. The number of possible combinations is astronomically large — far more than the number of atoms in the universe.

OR-Tools uses a technique called **CP-SAT** (Constraint Programming — SATisfiability) to navigate this search space intelligently:

- It applies **constraint propagation**: when a variable is assigned a value, it immediately removes all values from other variables that would violate a constraint.
- It uses **heuristics** to decide which variable to try next and which value to assign first.
- It can **backtrack** when it reaches a dead end and try alternative paths.
- For soft constraints, it uses an **objective function** to maximize the overall quality of the solution.

Despite these optimizations, some configurations can take longer:

- **Very tight constraints** (many teachers with overlapping unavailability).
- **Large numbers of groups and subjects** (more variables and combinations).
- **Conflicting packs or shared hours** that reduce the search space but increase the complexity of each check.

In most real-world cases, the solver finds a solution within seconds or a couple of minutes. If it takes too long, consider reviewing your constraints or simplifying the configuration.

## 10. Constraints: HARD and SOFT

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

## 11. Common issues and how to solve them

### Error 11.1: no valid timetable can be generated

Check:

- Subjects without assigned teacher.
- Teachers with weekly maximum too low.
- Too many unavailable timeslots.
- Misconfigured packs or inconsistent shared hours.

### Error 11.2: a subject does not appear with expected hours

Check:

- Subject weekly hours.
- Whether it belongs to a Pack with constrained hours.
- Whether it is limited by max per day or consecutive/non-consecutive rules.

### Error 11.3: teacher overload

Check:

- Teacher weekly maximum.
- Subject distribution across more teachers.
- Overly restrictive availability.

### Error 11.4: tutor group conflict

Check:

- Tutor assignments in Teachers.
- That the same teacher is not overloaded with incompatible tutor group responsibilities.

## 12. Management best practices

- Keep naming consistent for courses, subjects, and packs.
- Create academic structure first, then teaching staff.
- Use shared hours only when there is a real pedagogical need.
- Avoid applying too many strict constraints to many teachers at once.
- Regenerate the timetable after each relevant block of changes.

## 13. Final checklist before generating

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
