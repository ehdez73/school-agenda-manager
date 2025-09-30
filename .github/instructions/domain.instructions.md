---
applyTo: '**'
---

# Domain Context
 - A school has several grades, e.g. 1st, 2nd, 3rd, etc.
 - Each grade can have several classes or groups (depending on the number of students), e.g. 1A, 1B, 1C, etc.
 - Each grade has several subjects, e.g. Maths 1st, Maths 2nd, Language 1st, Science 3rd, etc.
 - Each subject has a number of weekly hours depending on its workload, e.g. Maths 1st: 4 hours, Maths 2nd: 5 hours, Language 1st: 5 hours, etc.
 - There are several teachers, each can teach several subjects. e.g. John: Maths 1st and Maths 2nd, Jane: Science 1st. 
 - Each teacher has a maximum number of teaching hours per week.
 - The schedule covers from monday to friday (configurable) and each day has a limited number of teaching hours, defined by configuration, e.g. 5 hours/day forming a table of 5x5 slots.
 - Some slots are split to teach two or more subjects, for example (religion/ethics), so each slot will be associated with a “subject group” that includes one or more subjects.

 ## Mandatory constraints:
 - No teacher can be in two classes at the same time.
 - Respect the maximum number of hours per teacher.
 - Fulfill mandatory availability restrictions.
 - Cover all weekly hours for each subject.
 - Do not exceed the configured number of daily hours.
