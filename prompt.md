Help me define a prompt to solve the following problem related to a school timetable management program.
Specifically, I want you to help me solve the problem using ortools for timetable creation and AI agents (openai) for autonomous planning and execution.

Context:
 - A school has several grades, e.g. 1st, 2nd, 3rd, etc.
 - Each grade can have several classes (depending on the number of students), e.g. 1A, 1B, 1C, etc.
 - Each grade has several subjects, e.g. Math 1st, Math 2nd, Language 1st, Science 3rd, etc.
 - Each subject has a number of weekly hours depending on its workload, e.g. Math 1st 4 hours, Math 2nd 5 hours, Language 1st 5 hours, etc.
 - There are several teachers, each can teach several subjects.
 - Each teacher has a maximum number of teaching hours per week.
 - A teacher may have a series of mandatory restrictions that must always be met (e.g. "Cannot attend Thursday afternoons")
 - A teacher may have a series of preferences that should be met if possible, although not mandatory (e.g. "Try not to assign classes on Friday first period")
 - Each day has a limited number of teaching hours, defined by configuration, e.g. 5 hours/day
 - A weekly timetable (Monday to Friday) must be generated for all subjects and grades, taking into account the weekly hours of each subject and that a teacher cannot teach two classes at the same time.
 - Timetables should distribute subjects evenly throughout the week, avoiding concentrating all hours of a subject on a single day.
 - Timetables must be generated automatically.
 - The final result should be a clear and easy-to-understand timetable, showing which subject is taught in each grade, on which day and at what time, as well as the teacher in charge of each class.
 - Once the timetables are generated, a personalized timetable for each teacher will be created from the previous ones.
 - The timetable for each teacher (in markdown format) will be passed to an AI agent to check if their restrictions and/or preferences are met.

Mandatory constraints:
 - No teacher can be in two classes at the same time.
 - Respect the maximum number of hours per teacher.
 - Fulfill mandatory availability restrictions.
 - Cover all weekly hours for each subject.
 - Do not exceed the configured number of daily hours.

Timetable quality criteria:
 - Distribute the hours of each subject evenly (avoid concentrating them on a single day).
 - Try to respect teachers' preferences.
 - Avoid unnecessary gaps in the schedule for both grades and teachers.

Libraries to use:

You can use the following libraries to create tools:
 - ortools
 - anthropic
 - openai
 - openai-oagents
If necessary, you can use mcp.

