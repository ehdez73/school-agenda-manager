# Implementation Plan: Homogeneizacion de Maquetado del Frontend

**Branch**: `[001-homogeneizar-maquetado-frontend]` | **Date**: 2026-03-22 | **Spec**: [/specs/001-homogeneizar-maquetado-frontend/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-homogeneizar-maquetado-frontend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Estandarizar la estructura visual de las secciones principales del frontend para reducir inconsistencias de maquetado, preservar usabilidad en escritorio/movil y dejar reglas reutilizables para nuevas vistas. El enfoque combina un patron de layout transversal, consolidacion de estilos compartidos y validacion test-first para consistencia visual y no regresion funcional.

## Technical Context

**Language/Version**: JavaScript (ES Modules), React 19.1.x, Node runtime compatible con Vite 7.x  
**Primary Dependencies**: React, React DOM, Vite, CSS global + componentes, react-markdown (sin cambios de alcance funcional)  
**Storage**: N/A (sin cambios de persistencia; solo maquetado frontend)  
**Testing**: ESLint existente + pruebas frontend nuevas de layout (Vitest + React Testing Library) + validacion manual responsive  
**Target Platform**: Navegadores modernos en escritorio y movil  
**Project Type**: Aplicacion web (frontend React + backend Flask existente)  
**Performance Goals**: Mantener tiempo de render percibido sin degradacion visible; no introducir saltos de layout perceptibles al cargar secciones  
**Constraints**: Cumplir frontend/STYLING_GUIDE.md, evitar cambios de comportamiento en backend/scheduler, mantener accesibilidad basica (focus visible, contraste y jerarquia legible)  
**Scale/Scope**: Homogeneizacion de secciones principales en frontend/src/components y contenedor de pagina en frontend/src/App.jsx

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Domain fidelity preserved: el alcance es UI frontend y no altera modelo academico ni restricciones obligatorias de horarios.
- [x] Constraint modeling explicit: no hay cambios en restricciones CP-SAT ni indices de asignaciones.
- [x] Test-first evidence present: se planifican pruebas de layout/estructura que fallen primero antes de aplicar refactor visual.
- [x] API/schema integrity covered: no se planean cambios de contratos API ni schemas; cualquier desviacion se documentara y testeara.
- [x] Reproducible workflow preserved: se mantiene workflow del repositorio (uv en backend, npm/vite en frontend) sin alterar comandos base.
- [x] No constitution violations remain, or each violation is documented in Complexity Tracking with explicit justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-homogeneizar-maquetado-frontend/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app.py
├── scheduler.py
├── schemas.py
├── restrictions/
└── test/

frontend/
├── src/
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   ├── styles/
│   │   ├── globals.css
│   │   ├── utilities.css
│   │   └── components.css
│   └── components/
│       ├── Shared.css
│       ├── *List.jsx
│       ├── *List.css
│       ├── *Form.jsx
│       └── *.css
└── package.json
```

**Structure Decision**: Se usa estructura de aplicacion web existente (frontend + backend). El trabajo de esta feature se concentra en frontend/src/App.jsx, frontend/src/App.css, frontend/src/components/* y frontend/src/styles/*, manteniendo backend sin cambios funcionales.

## Phase 0 Research Output

Resultado consolidado en [/specs/001-homogeneizar-maquetado-frontend/research.md](./research.md) con decisiones sobre patron base de layout, estrategia de estilos compartidos, validacion test-first y criterios responsive.

## Phase 1 Design Output

- Modelo de dominio de interfaz: [/specs/001-homogeneizar-maquetado-frontend/data-model.md](./data-model.md)
- Contrato de maquetado y estados: [/specs/001-homogeneizar-maquetado-frontend/contracts/frontend-layout-contract.md](./contracts/frontend-layout-contract.md)
- Guia de ejecucion/validacion: [/specs/001-homogeneizar-maquetado-frontend/quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- [x] Domain fidelity preserved after design: no se introducen cambios a reglas academicas ni solver.
- [x] Constraint modeling remains explicit: diseno circunscrito a frontend, sin tocar backend/restrictions.
- [x] Test-first validation remains planned: quickstart define paso de pruebas fallando antes de refactor.
- [x] API/schema integrity reconfirmed: contrato de API no cambia en este diseno.
- [x] Reproducible workflow maintained: comandos de frontend/backend se mantienen segun convenciones del repo.

## Complexity Tracking

Sin violaciones detectadas.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
