# Quickstart: Homogeneizacion de Maquetado del Frontend

## Objective

Implementar y validar una maquetacion consistente para las secciones principales del frontend sin alterar comportamiento de negocio del backend.

## Prerequisites

- Node y npm disponibles para frontend.
- Python/uv disponibles para validar backend sin regresiones colaterales.
- Rama activa: 001-homogeneizar-maquetado-frontend.

## 1) Baseline and Install

```bash
cd frontend
npm install
```

## 2) Run frontend locally

```bash
cd frontend
npm run dev
```

## 3) Test-first workflow (required)

1. Definir pruebas de estructura por seccion (header/content/actions + estados).
2. Ejecutar pruebas y confirmar fallo inicial antes de aplicar cambios de maquetado.
3. Aplicar refactor de layout compartido y estilos.
4. Re-ejecutar pruebas hasta que pasen.

Comando previsto para pruebas frontend (tras agregar setup de tests):

```bash
cd frontend
npm run test
```

## 4) Lint and visual verification

```bash
cd frontend
npm run lint
```

Validacion manual minima:
- Navegar por secciones objetivo y confirmar patron base comun.
- Verificar estados loading/empty/error/ready.
- Revisar escritorio y movil para jerarquia y espaciado.

## 5) Regression guard for backend

Aunque no hay cambios de backend en alcance, ejecutar smoke de tests existentes:

```bash
cd backend
uv run python -m pytest test/test_routes.py test/test_timetable.py
```

## 6) Definition of done

- Patron de maquetado aplicado en todas las secciones objetivo.
- Pruebas de layout pasan.
- Lint pasa.
- Sin cambios de contrato API/schemas.
- Sin regresiones funcionales en flujos principales.

## 7) Execution Results (Current Iteration)

Automated validation executed in this branch:

- Frontend lint: `npm run lint` -> PASS.
- Frontend full tests: `npm test` -> PASS (`12` files, `50` tests).
- Backend smoke tests: `uv run python -m pytest test/test_routes.py test/test_timetable.py` -> PASS (`7` tests).

Additional focused suites:

- US2 contract tests (`SectionLayout` header/actions/states): PASS (`19` tests).
- US3 responsive tests: PASS (`5` tests).
- Regression guards:
	- `src/components/__tests__/lists.regression.test.jsx` -> PASS (`4` tests).
	- `src/components/__tests__/forms.regression.test.jsx` -> PASS (`2` tests).

## 8) Manual Validation Checklist (Desktop/Mobile)

Scope validated manually by QA/Product in browser:

- [ ] Desktop: header/content/actions hierarchy looks consistent across CourseList, SubjectList, SubjectGroupList, TeacherList, ConfigForm, MarkdownTimetable.
- [ ] Mobile (<=768px): actions stack correctly and controls remain usable.
- [ ] Section states (loading/error/empty) are readable and visually consistent.
- [ ] No visual regressions in CRUD primary actions (add/edit/delete entrypoints).

Status at the end of this implementation run:

- Automated checks: complete.
- Manual desktop/mobile walkthrough: pending execution by QA/Product.

## 9) Internal Consistency Evaluation Protocol (SC-002)

Objective:

- Verify that at least 90% of participants perceive the UI as consistent when navigating between target sections.

Protocol:

1. Sample size: minimum `10` internal participants (Product, QA, Development).
2. Task: navigate all target sections and identify primary action in each one.
3. Survey scale: Likert 1-5 where `4` and `5` count as "consistent".
4. Acceptance criterion: `consistent_responses / total_responses >= 0.90`.

Data capture template:

| Participant | Score (1-5) | Counts as Consistent (Y/N) |
|-------------|-------------|----------------------------|
| P01         |             |                            |
| P02         |             |                            |
| ...         |             |                            |
| P10         |             |                            |

Compliance formula:

- $SC002 = \frac{N_{score\ge4}}{N_{total}}$
- Pass if $SC002 \ge 0.90$.

Current status:

- Data collection pending.

## 10) Time-to-Action Measurement Protocol (SC-003)

Objective:

- Verify that mean time to locate and execute the primary action is reduced by at least 20%.

Protocol:

1. Participants: minimum `5` internal users.
2. Device/profile parity: same device class, same participant profile pre/post.
3. Tasks per section: locate and execute the primary action in at least 3 target sections.
4. Record baseline (`before`) and post-change (`after`) in seconds.

Baseline table template:

| User | Section | Before (s) | After (s) | Reduction % |
|------|---------|------------|-----------|-------------|
| U01  | Courses |            |           |             |
| U01  | Subjects|            |           |             |
| U01  | Teachers|            |           |             |
| ...  | ...     |            |           |             |

Computation:

- $Reduction\% = \frac{Before - After}{Before} \times 100$
- $SC003 = mean(Reduction\%)$
- Pass if $SC003 \ge 20\%$.

Current status:

- Baseline and post-change measurements pending manual run.
