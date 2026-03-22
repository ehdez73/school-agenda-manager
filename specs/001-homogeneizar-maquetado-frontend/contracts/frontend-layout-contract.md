# Frontend Layout Contract

## Scope

Contrato de interfaz para asegurar homogeneidad de maquetado en secciones principales del frontend.

Secciones objetivo iniciales:
- CourseList
- SubjectList
- SubjectGroupList
- TeacherList
- ConfigForm
- MarkdownTimetable

## Contract Rules

### 1. Section Frame

Cada seccion MUST exponer una estructura base con:
- Header container.
- Main content container.
- Action area (si existen acciones).

### 2. Header Semantics

- Debe existir un titulo principal visible.
- La descripcion es opcional, pero su posicion debe ser consistente.
- Acciones de nivel seccion no deben romper alineacion del titulo.

### 3. Action Hierarchy

- Debe existir maximo una accion primaria visual por seccion.
- Acciones secundarias deben ser distinguibles y mantener orden consistente.
- En movil, las acciones mantienen jerarquia aunque cambie disposicion.

### 4. State Presentation

Para cada seccion se define render consistente de estados:
- loading: indicador de carga y contexto de seccion.
- empty: mensaje claro y accion recomendada.
- error: mensaje de fallo y accion de recuperacion.
- ready: contenido principal operativo.

### 5. Spacing and Alignment

- Espaciado vertical entre header, contenido y acciones debe usar tokens globales.
- Margenes y paddings ad hoc deben eliminarse salvo excepcion documentada.
- Layout debe conservar legibilidad en breakpoints utilizados por el producto.

### 6. Accessibility Baseline

- Focus visible en controles interactivos.
- Orden de tabulacion coherente con jerarquia visual.
- Contraste compatible con reglas base del proyecto.

## Verification Checklist

- Cada seccion cumple Section Frame.
- Cada seccion declara y renderiza estados loading/empty/error/ready.
- La accion primaria se identifica sin ambiguedad.
- No se detectan regresiones funcionales en CRUD basico de listas/formularios.
- Comportamiento en movil y escritorio validado para secciones del alcance.
