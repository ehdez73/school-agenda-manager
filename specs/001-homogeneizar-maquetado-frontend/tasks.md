# Tasks: Homogeneizacion de Maquetado del Frontend

**Input**: Design documents from /specs/001-homogeneizar-maquetado-frontend/
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/frontend-layout-contract.md, quickstart.md

**Tests**: Test-first obligatorio por constitucion del proyecto. Cada historia incluye tareas de pruebas que deben fallar antes de implementar.

**Organization**: Tareas agrupadas por historia de usuario para implementar y validar cada incremento de forma independiente.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar tooling y base de pruebas frontend para ejecutar workflow test-first.

- [X] T001 Revisar y documentar alcance de secciones objetivo en specs/001-homogeneizar-maquetado-frontend/contracts/frontend-layout-contract.md
- [X] T002 Agregar dependencias de pruebas frontend (vitest, @vitest/coverage-v8, @testing-library/react, @testing-library/jest-dom, jsdom) en frontend/package.json
- [X] T003 [P] Crear configuracion de Vitest con entorno jsdom en frontend/vitest.config.js
- [X] T004 [P] Crear setup global de pruebas con importacion de @testing-library/jest-dom en frontend/src/test/setupTests.js
- [X] T005 [P] Crear script de pruebas en frontend/package.json
- [X] T006 Validar instalacion de dependencias y ejecucion inicial de pruebas frontend desde frontend/package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Definir infraestructura de layout compartido que bloquea todas las historias.

**CRITICAL**: Ninguna historia puede empezar antes de completar esta fase.

- [X] T007 Crear componente base de layout de seccion en frontend/src/components/SectionLayout.jsx
- [X] T008 [P] Crear estilos compartidos de layout de seccion en frontend/src/components/SectionLayout.css
- [X] T009 [P] Definir tokens y utilidades de espaciado transversales en frontend/src/styles/globals.css
- [X] T010 [P] Añadir utilidades de composicion de bloques en frontend/src/styles/utilities.css
- [X] T011 Estandarizar primitivas visuales de encabezado y acciones en frontend/src/styles/components.css
- [X] T012 Definir helpers compartidos para estados loading/empty/error/ready en frontend/src/components/Shared.css
- [X] T013 Integrar estilos base del nuevo layout en frontend/src/index.css
- [X] T014 Crear fixture de validacion de estructura para secciones en frontend/src/test/layoutFixtures.js

**Checkpoint**: Fundacion de layout lista; las historias pueden ejecutarse.

---

## Phase 3: User Story 1 - Experiencia visual consistente (Priority: P1) MVP

**Goal**: Unificar estructura visual de secciones principales existentes para navegacion coherente.

**Independent Test**: Navegar entre listas y confirmar estructura comun header-content-actions sin romper flujos CRUD.

### Tests for User Story 1 (REQUIRED)

- [X] T015 [P] [US1] Crear prueba de estructura base para CourseList en frontend/src/components/__tests__/CourseList.layout.test.jsx
- [X] T016 [P] [US1] Crear prueba de estructura base para SubjectList en frontend/src/components/__tests__/SubjectList.layout.test.jsx
- [X] T017 [P] [US1] Crear prueba de estructura base para SubjectGroupList en frontend/src/components/__tests__/SubjectGroupList.layout.test.jsx
- [X] T018 [P] [US1] Crear prueba de estructura base para TeacherList en frontend/src/components/__tests__/TeacherList.layout.test.jsx
- [X] T019 [US1] Ejecutar pruebas de layout y confirmar fallo inicial en frontend/src/components/__tests__/CourseList.layout.test.jsx

### Implementation for User Story 1

- [X] T020 [P] [US1] Refactorizar CourseList para usar SectionLayout en frontend/src/components/CourseList.jsx
- [X] T021 [P] [US1] Refactorizar SubjectList para usar SectionLayout en frontend/src/components/SubjectList.jsx
- [X] T022 [P] [US1] Refactorizar SubjectGroupList para usar SectionLayout en frontend/src/components/SubjectGroupList.jsx
- [X] T023 [P] [US1] Refactorizar TeacherList para usar SectionLayout en frontend/src/components/TeacherList.jsx
- [X] T024 [US1] Homogeneizar estilos de listas y cabeceras en frontend/src/components/CourseList.css
- [X] T025 [US1] Homogeneizar estilos de listas y cabeceras en frontend/src/components/SubjectList.css
- [X] T026 [US1] Homogeneizar estilos de listas y cabeceras en frontend/src/components/SubjectGroupList.css
- [X] T027 [US1] Homogeneizar estilos de listas y cabeceras en frontend/src/components/TeacherList.css
- [X] T028 [US1] Ajustar contenedor principal para consistencia global en frontend/src/App.css
- [X] T029 [US1] Re-ejecutar pruebas de US1 y validar paso en frontend/src/components/__tests__/TeacherList.layout.test.jsx

**Checkpoint**: US1 funcional y testeable de forma independiente.

---

## Phase 4: User Story 2 - Creacion de nuevas vistas alineadas (Priority: P2)

**Goal**: Dejar reglas y composicion reutilizable para nuevas secciones sin variaciones ad hoc.

**Independent Test**: Implementar una seccion de referencia con patron definido y validar que no requiere excepciones visuales.

### Tests for User Story 2 (REQUIRED)

- [ ] T030 [P] [US2] Crear prueba del contrato de header semantico en frontend/src/components/__tests__/SectionLayout.header-contract.test.jsx
- [X] T030 [P] [US2] Crear prueba del contrato de header semantico en frontend/src/components/__tests__/SectionLayout.header-contract.test.jsx
- [X] T031 [P] [US2] Crear prueba del contrato de jerarquia de acciones en frontend/src/components/__tests__/SectionLayout.actions-contract.test.jsx
- [X] T032 [P] [US2] Crear prueba del contrato de estados loading-empty-error-ready en frontend/src/components/__tests__/SectionLayout.states-contract.test.jsx
- [X] T033 [US2] Ejecutar pruebas de contrato y confirmar fallo inicial en frontend/src/components/__tests__/SectionLayout.actions-contract.test.jsx

### Implementation for User Story 2

- [ ] T034 [US2] Implementar API de composicion del SectionLayout en frontend/src/components/SectionLayout.jsx
- [X] T034 [US2] Implementar API de composicion del SectionLayout en frontend/src/components/SectionLayout.jsx
- [X] T035 [US2] Incorporar soporte de estados comunes en frontend/src/components/SectionLayout.jsx
- [X] T036 [P] [US2] Refactorizar ConfigForm para utilizar patron de seccion en frontend/src/components/ConfigForm.jsx
- [X] T037 [P] [US2] Refactorizar MarkdownTimetable para utilizar patron de seccion en frontend/src/components/MarkdownTimetable.jsx
- [X] T038 [US2] Homogeneizar estilos de ConfigForm con tokens compartidos en frontend/src/components/ConfigForm.css
- [X] T039 [US2] Homogeneizar estilos de MarkdownTimetable con tokens compartidos en frontend/src/components/MarkdownTimetable.css
- [X] T040 [US2] Documentar reglas de maquetado para nuevas vistas en frontend/STYLING_GUIDE.md
- [X] T041 [US2] Re-ejecutar pruebas de contrato y validar paso en frontend/src/components/__tests__/SectionLayout.states-contract.test.jsx

**Checkpoint**: US2 funcional y reusable para nuevas vistas.

---

## Phase 5: User Story 3 - Consistencia en distintos tamanos de pantalla (Priority: P3)

**Goal**: Garantizar consistencia de jerarquia visual y legibilidad en escritorio y movil.

**Independent Test**: Validar en viewport desktop y mobile que el orden y jerarquia de bloques se mantiene.

### Tests for User Story 3 (REQUIRED)

- [X] T042 [P] [US3] Crear prueba responsive para listas en frontend/src/components/__tests__/SectionLayout.responsive-lists.test.jsx
- [X] T043 [P] [US3] Crear prueba responsive para formularios en frontend/src/components/__tests__/SectionLayout.responsive-forms.test.jsx
- [X] T044 [P] [US3] Crear prueba responsive para markdown timetable en frontend/src/components/__tests__/SectionLayout.responsive-markdown.test.jsx
- [X] T045 [US3] Ejecutar pruebas responsive y confirmar fallo inicial en frontend/src/components/__tests__/SectionLayout.responsive-lists.test.jsx

### Implementation for User Story 3

- [X] T046 [US3] Definir breakpoints y reglas responsive para SectionLayout en frontend/src/components/SectionLayout.css
- [X] T047 [P] [US3] Ajustar acciones y header en movil para listas en frontend/src/components/CourseList.css
- [X] T048 [P] [US3] Ajustar acciones y header en movil para formularios en frontend/src/components/ConfigForm.css
- [X] T049 [P] [US3] Ajustar bloques markdown en movil en frontend/src/components/MarkdownTimetable.css
- [X] T050 [US3] Asegurar coherencia responsive del contenedor principal en frontend/src/App.css
- [X] T051 [US3] Re-ejecutar pruebas responsive y validar paso en frontend/src/components/__tests__/SectionLayout.responsive-markdown.test.jsx

**Checkpoint**: US3 funcional y validada en escritorio/movil.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cierre de calidad, regresion y validacion final.

- [X] T052 [P] Ejecutar lint frontend y corregir hallazgos en frontend/package.json
- [X] T053 Ejecutar suite completa de pruebas frontend en frontend/package.json
- [X] T054 [P] Ejecutar smoke tests backend sin cambios de contrato en backend/test/test_routes.py
- [X] T055 Ejecutar smoke tests backend sin cambios de contrato en backend/test/test_timetable.py
- [ ] T056 Documentar resultados de validacion manual desktop/mobile en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [X] T057 Definir protocolo de evaluacion interna de consistencia visual (muestra, encuesta y criterio de aprobacion) en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [ ] T058 Ejecutar evaluacion interna de consistencia visual y consolidar resultados en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [ ] T059 Verificar cumplimiento de SC-002 con evidencia cuantitativa en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [X] T060 Definir baseline de tiempo para accion principal por seccion objetivo en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [ ] T061 Medir tiempo post-cambio y calcular variacion porcentual en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [ ] T062 Verificar cumplimiento de SC-003 con evidencia cuantitativa en specs/001-homogeneizar-maquetado-frontend/quickstart.md
- [X] T063 [P] Crear pruebas de no regresion funcional para listas CRUD en frontend/src/components/__tests__/lists.regression.test.jsx
- [X] T064 [P] Crear pruebas de no regresion funcional para formularios principales en frontend/src/components/__tests__/forms.regression.test.jsx
- [X] T065 Ejecutar suite de no regresion frontend y registrar resultados en specs/001-homogeneizar-maquetado-frontend/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): inicia inmediatamente.
- Foundational (Phase 2): depende de Setup y bloquea todas las historias.
- User Stories (Phases 3-5): dependen de Foundational.
- Polish (Phase 6): depende de completar historias objetivo.

### User Story Dependencies

- US1 (P1): inicia tras Foundational, sin dependencia de otras historias.
- US2 (P2): inicia tras Foundational; reutiliza SectionLayout y puede convivir con US1.
- US3 (P3): inicia tras Foundational; depende de layout compartido consolidado.

### Within Each User Story

- Pruebas primero y en rojo antes de implementar.
- Refactor de componentes despues de pruebas.
- Ajustes de estilos despues del refactor estructural.
- Re-ejecucion de pruebas y cierre de historia.

## Parallel Opportunities

- T003, T004, T005 pueden ejecutarse en paralelo.
- T008, T009, T010 pueden ejecutarse en paralelo.
- En US1, T015-T018 y luego T020-T023 pueden ejecutarse en paralelo por componente.
- En US2, T030-T032 y luego T036-T037 pueden ejecutarse en paralelo.
- En US3, T042-T044 y luego T047-T049 pueden ejecutarse en paralelo.
- En Polish, T052 y T054 pueden ejecutarse en paralelo.
- En Polish, T063 y T064 pueden ejecutarse en paralelo.

## Parallel Example: User Story 1

- Ejecutar en paralelo: T015, T016, T017, T018.
- Ejecutar en paralelo tras pruebas en rojo: T020, T021, T022, T023.

## Parallel Example: User Story 2

- Ejecutar en paralelo: T030, T031, T032.
- Ejecutar en paralelo tras contrato base: T036, T037.

## Parallel Example: User Story 3

- Ejecutar en paralelo: T042, T043, T044.
- Ejecutar en paralelo tras reglas responsive base: T047, T048, T049.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1 y Phase 2.
2. Completar US1 con pruebas primero.
3. Validar independiente y demostrar consistencia en listas.

### Incremental Delivery

1. Setup + Foundational.
2. Entregar US1 y validar.
3. Entregar US2 y validar.
4. Entregar US3 y validar.
5. Cerrar con Polish y smoke backend.

### Parallel Team Strategy

1. Equipo completo en Setup + Foundational.
2. Luego reparto por historia:
   - Persona A: US1.
   - Persona B: US2.
   - Persona C: US3.
3. Integracion final en Phase 6.
