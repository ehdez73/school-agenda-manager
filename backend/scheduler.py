from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar
from .models import (
    Session,
    Teacher,
    Subject,
    Course,
    Config,
    Timeslot,
    TimeSlotAssignment,
    SubjectGroup,
)
from .timetable import (
    print_markdown_timetable_from_assignments,
    print_markdown_timetable_per_teacher,
)
from .populate_db import populate_db
from .restrictions import (
    SubjectWeeklyHours,
    TeacherOneClassAtATime,
    TeacherMaxWeeklyHours,
    GroupSubjectMaxHoursPerDay,
    GroupAtMostOneLogicalAssignment,
    GroupSubjectHoursMustBeConsecutive,
    SubjectGroupAssignment,
    TeacherUnavailableTimes,
    TeacherPreferredTimes,
    TutorPreference,
)


def save_solution_to_db(
    session, solver, assignments, groups, subjects, teachers, num_days, num_hours
):
    # Clear previous schedule
    session.query(TimeSlotAssignment).delete()
    session.query(Timeslot).delete()
    session.commit()

    print("Saving solution to the database...")
    for d in range(num_days):
        for h in range(num_hours):
            for group in groups:
                course_id, line_str = group.split("-")
                line_num = ord(line_str) - ord("A")

                # store day as integer index `d` (0 = first weekday)
                timeslot = Timeslot(day=d, hour=h, course_id=course_id, line=line_num)
                session.add(timeslot)

                for key in assignments:
                    if (
                        key[0] == group
                        and key[3] == d
                        and key[4] == h
                        and solver.Value(assignments[key]) == 1
                    ):
                        _, subject_id, teacher_id, _, _ = key
                        assignment = TimeSlotAssignment(
                            timeslot=timeslot,
                            subject_id=subject_id,
                            teacher_id=teacher_id,
                        )
                        session.add(assignment)
    session.commit()
    print("Timetable saved to the database.")


def get_contrainsts_violated(model, solver):
    violated = []
    violated.append("# ❌ No solution was found for the given constraints\n")
    violated.append("## Violated constraints:\n")

    failed_assumption_indexes = solver.sufficient_assumptions_for_infeasibility()
    failed_assumptions_causes = [
        model.get_bool_var_from_proto_index(i).name for i in failed_assumption_indexes
    ]

    for cause in failed_assumptions_causes:
        violated.append(f"* {cause}\n")

    return "".join(violated)


def solve_scheduling_model(
    all_teachers, all_subjects, all_groups, all_subjectgroups, num_days, num_hours
):
    """
    Builds and solves the scheduling model without requiring a database session.

    Args:
        all_teachers: List of Teacher objects
        all_subjects: List of Subject objects
        all_groups: List of group identifiers (e.g., "1-A", "1-B")
        all_subjectgroups: List of SubjectGroup objects
        num_days: Number of days per week
        num_hours: Number of hours per day

    Returns:
        Tuple of (status, assignments, solver) where:
        - status: CP-SAT solver status (OPTIMAL, FEASIBLE, or INFEASIBLE)
        - assignments: Dictionary of decision variables
        - solver: The solver object with the solution
    """
    # --- 1. Model Initialization ---
    model = cp_model.CpModel()

    # Create decision variables (group-subject-teacher-day-hour)
    assignments = {}
    for group in all_groups:
        course = group.split("-")[0]
        for subject in all_subjects:
            if subject.course_id == course:
                for teacher in all_teachers:
                    if subject in teacher.subjects:
                        for d in range(num_days):
                            for h in range(num_hours):
                                key = (group, subject.id, teacher.id, d, h)
                                assignments[key] = model.NewBoolVar(
                                    f"g:{group} sub:{subject.id} t:{teacher.name} d:{d} h:{h}"
                                )

    # Apply restrictions
    SubjectWeeklyHours().apply(model, assignments, all_groups, all_subjects)
    TeacherOneClassAtATime().apply(
        model, assignments, all_teachers, num_days, num_hours
    )
    TeacherUnavailableTimes().apply(
        model, assignments, all_teachers, num_days, num_hours
    )
    TeacherMaxWeeklyHours().apply(model, assignments, all_teachers)
    GroupSubjectMaxHoursPerDay().apply(
        model, assignments, all_groups, all_subjects, all_teachers, num_days
    )
    GroupAtMostOneLogicalAssignment().apply(
        model, assignments, all_groups, num_days, num_hours, all_subjectgroups
    )
    GroupSubjectHoursMustBeConsecutive().apply(
        model, assignments, all_groups, all_subjects, num_days, num_hours
    )
    SubjectGroupAssignment().apply(
        model, assignments, all_groups, all_subjects, all_subjectgroups
    )

    # Apply teacher preferences
    teacher_preferred = TeacherPreferredTimes()
    teacher_preferred.apply(model, assignments, all_teachers, num_days, num_hours)

    # Apply tutor preference
    tutor_pref = TutorPreference()
    tutor_pref.apply(model, assignments, all_teachers)

    # Combine all preference terms for objective
    preference_terms = teacher_preferred.preference_terms + tutor_pref.preference_terms
    if preference_terms:
        model.Maximize(sum(preference_terms))

    # --- 2. Solve ---
    print("\n🧠 Starting the solver... This may take a moment.")
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0  # Set a time limit
    status = solver.Solve(model)

    return status, assignments, solver


def create_timetable(session) -> str | None:
    """
    Generates the school timetable using the OR-Tools CP-SAT solver.

    This is the main entry point that:
    1. Loads data from the database
    2. Calls solve_scheduling_model to build and solve the model
    3. Saves the results to the database
    """

    # --- 1. Data Loading ---
    all_teachers = session.query(Teacher).all()
    all_subjects = session.query(Subject).all()
    all_courses = session.query(Course).all()
    all_subjectgroups = session.query(SubjectGroup).all()
    config = session.query(Config).first()

    # Create default configuration if none exists
    if not config:
        print("⚙️  No configuration found, creating default configuration...")
        config = Config(
            classes_per_day=5, days_per_week=5
        )  # Default: 5 classes per day, 5 days per week
        session.add(config)
        session.commit()
        print(
            f"✅ Default configuration created: {config.classes_per_day} classes per day"
        )

    num_days = config.days_per_week
    num_hours = config.classes_per_day

    # Create a unique list of all class groups (1ºA, 1ºB, 2ºA, etc.)
    all_groups = []
    for course in all_courses:
        for i in range(course.num_lines):
            line_char = chr(ord("A") + i)
            all_groups.append(f"{course.id}-{line_char}")

    # --- 2. Solve the scheduling model ---
    status, assignments, solver = solve_scheduling_model(
        all_teachers, all_subjects, all_groups, all_subjectgroups, num_days, num_hours
    )

    # --- 3. Solution Processing ---
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✅ Solution found!")
        save_solution_to_db(
            session,
            solver,
            assignments,
            all_groups,
            all_subjects,
            all_teachers,
            num_days,
            num_hours,
        )
        session.close()
        return None
    else:
        # Get the model for error reporting
        # We need to rebuild it to get the model for error analysis
        model = cp_model.CpModel()
        assignments_temp = {}
        for group in all_groups:
            course = group.split("-")[0]
            for subject in all_subjects:
                if subject.course_id == course:
                    for teacher in all_teachers:
                        if subject in teacher.subjects:
                            for d in range(num_days):
                                for h in range(num_hours):
                                    key = (group, subject.id, teacher.id, d, h)
                                    assignments_temp[key] = model.NewBoolVar(
                                        f"g:{group} sub:{subject.id} t:{teacher.name} d:{d} h:{h}"
                                    )

        SubjectWeeklyHours().apply(model, assignments_temp, all_groups, all_subjects)
        TeacherOneClassAtATime().apply(
            model, assignments_temp, all_teachers, num_days, num_hours
        )
        TeacherUnavailableTimes().apply(
            model, assignments_temp, all_teachers, num_days, num_hours
        )
        TeacherMaxWeeklyHours().apply(model, assignments_temp, all_teachers)
        GroupSubjectMaxHoursPerDay().apply(
            model, assignments_temp, all_groups, all_subjects, all_teachers, num_days
        )
        GroupAtMostOneLogicalAssignment().apply(
            model, assignments_temp, all_groups, num_days, num_hours, all_subjectgroups
        )
        GroupSubjectHoursMustBeConsecutive().apply(
            model, assignments_temp, all_groups, all_subjects, num_days, num_hours
        )
        SubjectGroupAssignment().apply(
            model, assignments_temp, all_groups, all_subjects, all_subjectgroups
        )

        return get_contrainsts_violated(model, solver)


if __name__ == "__main__":
    populate_db()  # Populate the database with initial data
    session = Session()
    result = create_timetable(session)
    if result is None:  # Success
        print(print_markdown_timetable_from_assignments(session))
        print("\n" + "=" * 50)
        print(print_markdown_timetable_per_teacher(session))
    else:  # Error
        print(result)
