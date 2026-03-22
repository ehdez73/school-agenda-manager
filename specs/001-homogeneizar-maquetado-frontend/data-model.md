# Data Model: Homogeneizacion de Maquetado del Frontend

Este feature no introduce entidades persistentes nuevas. Define un modelo de dominio de interfaz para guiar implementacion y validacion.

## Entity: SectionLayout

- Purpose: Representa la estructura visual canonica de una seccion del frontend.
- Fields:
  - sectionId: identificador estable de la seccion (ej. courses, subjects, teachers).
  - header: bloque de encabezado (titulo, descripcion opcional, acciones contextuales).
  - content: bloque principal con lista/formulario/rejilla.
  - actions: conjunto de acciones primarias y secundarias con jerarquia definida.
  - spacingProfile: reglas de espaciado vertical y horizontal aplicables.
  - responsiveRules: reglas de reflujo entre escritorio y movil.
- Validation rules:
  - Debe incluir header y content.
  - Debe declarar orden de acciones para evitar inconsistencias entre secciones.
  - Debe mapear al menos un estado de visualizacion.

## Entity: SectionViewState

- Purpose: Define como se presenta una seccion segun su estado operativo.
- Fields:
  - state: loading | empty | error | ready.
  - message: texto principal del estado.
  - secondaryInfo: detalle opcional.
  - availableActions: acciones permitidas en ese estado.
  - ariaHints: apoyo de accesibilidad para lectores de pantalla.
- Validation rules:
  - Cada seccion debe cubrir al menos empty y error ademas de ready.
  - loading no debe ocultar el contexto de navegacion de la seccion.

## Entity: LayoutRule

- Purpose: Regla reusable que aplica al conjunto de secciones.
- Fields:
  - ruleId: identificador de regla.
  - scope: global | list-sections | form-sections | markdown-sections.
  - requirement: declaracion verificable de estructura/espaciado/jerarquia.
  - acceptanceCheck: criterio objetivo de validacion (test o checklist verificable).
- Validation rules:
  - Cada regla debe ser medible y no ambigua.
  - Debe poder verificarse de forma automatizada o con checklist estandar.

## Relationships

- SectionLayout 1..* -> SectionViewState.
- SectionLayout 1..* -> LayoutRule (por alcance).
- LayoutRule puede aplicar a multiples SectionLayout.

## State Transitions

- SectionViewState transitions esperadas:
  - loading -> ready
  - loading -> empty
  - loading -> error
  - error -> loading (reintento)
  - empty -> loading (actualizacion/reintento)
