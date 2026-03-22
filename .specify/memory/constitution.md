<!--
Sync Impact Report
- Version change: template-placeholder -> 1.0.0
- Modified principles:
	- Template Principle 1 -> I. Scheduling Domain Fidelity
	- Template Principle 2 -> II. Deterministic Constraint Modeling
	- Template Principle 3 -> III. Test-First Validation (NON-NEGOTIABLE)
	- Template Principle 4 -> IV. Contracted API and Schema Integrity
	- Template Principle 5 -> V. Reproducible Developer Workflow
- Added sections:
	- Engineering Constraints
	- Delivery Workflow and Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ updated: .specify/templates/spec-template.md
	- ✅ updated: .specify/templates/tasks-template.md
	- ✅ updated: .specify/templates/constitution-template.md
	- ✅ updated: .specify/templates/agent-file-template.md
	- ✅ updated: .specify/templates/checklist-template.md
	- ⚠ pending: .specify/templates/commands/*.md (directory not present)
- Follow-up TODOs:
	- None
-->

# School Agenda Manager Constitution

## Core Principles

### I. Scheduling Domain Fidelity
All product and engineering changes MUST preserve the school scheduling domain model: grades,
groups/classes, subjects with weekly hours, teachers with capacity, configurable school week/day
slots, and subject-group slots. Mandatory scheduling constraints (teacher exclusivity per slot,
teacher max weekly hours, availability restrictions, subject weekly hour coverage, and daily hour
limits) MUST remain satisfiable and enforceable.
Rationale: The product exists to generate feasible school timetables; violating domain rules
invalidates outcomes regardless of implementation quality.

### II. Deterministic Constraint Modeling
Constraint logic MUST be implemented as explicit, composable restrictions under backend/restrictions
and wired through backend/scheduler.py using stable assignment indexing
(group, subject_id, teacher_id, day, hour). Solver-facing changes MUST avoid hidden side effects,
MUST document assumptions in code or tests, and MUST keep outputs reproducible for identical inputs.
Rationale: Constraint systems are difficult to debug when behavior is implicit; deterministic modeling
enables reliable diagnosis and maintenance.

### III. Test-First Validation (NON-NEGOTIABLE)
Every behavior change MUST include tests that fail before implementation and pass after implementation.
Restriction changes MUST include focused feasibility/infeasibility tests. Route or serialization changes
MUST include API/schema tests. Regressions in mandatory constraints are release blockers.
Rationale: Scheduling correctness is emergent from many constraints, so automated checks are mandatory
to prevent silent regressions.

### IV. Contracted API and Schema Integrity
Backend responses MUST be validated through shared schemas in backend/schemas.py and remain compatible
with frontend consumption patterns unless an explicit, versioned contract change is approved.
Any contract change MUST update tests, relevant docs, and affected UI rendering paths.
Rationale: The scheduler, API, and UI are tightly coupled; schema drift causes user-facing breakage.

### V. Reproducible Developer Workflow
Python backend setup and execution MUST use uv commands from backend/ (uv sync, uv run ...).
Contributors MUST prefer small, focused changes, preserve existing style, and keep tooling and docs
accurate for local and Docker workflows.
Rationale: Reproducible environments and disciplined scope reduce integration friction and debugging time.

## Engineering Constraints

- The canonical backend architecture is Flask + SQLAlchemy + OR-Tools CP-SAT + Pydantic schemas.
- New restrictions MUST subclass Restriction and live in backend/restrictions/ with adjacent tests.
- Frontend styling changes MUST follow frontend/STYLING_GUIDE.md unless superseded by an approved
	design-system update.
- Generated timetables MUST respect configured school days and daily hours; no hardcoded Monday-Friday
	assumptions may be introduced unless configuration says so.

## Delivery Workflow and Quality Gates

1. Scope and constraints are captured in spec artifacts before implementation starts.
2. The implementation plan MUST pass a constitution check before design and task generation proceed.
3. Pull requests MUST include: changed behavior summary, tests executed, and impacted constraints/contracts.
4. Merges are blocked when mandatory tests fail or when domain constraints become unverified.
5. Docs impacting contributor workflow MUST be updated in the same change set.

## Governance
This constitution supersedes conflicting local practices for planning and implementation.
Amendments require: (1) a written proposal, (2) review by maintainers, and (3) synchronization of
affected templates and guidance files in the same update.

Versioning policy:
- MAJOR: Removal or redefinition of a core principle or governance model change that breaks prior process.
- MINOR: New principle/section or materially expanded mandatory guidance.
- PATCH: Clarifications, wording improvements, typo fixes, or non-semantic edits.

Compliance review expectations:
- Every implementation plan MUST include and pass constitution gates.
- Every task list MUST map work to user stories and include required validation tasks.
- Reviewers MUST reject changes that violate non-negotiable principles without an approved amendment.

**Version**: 1.0.0 | **Ratified**: 2026-03-22 | **Last Amended**: 2026-03-22
