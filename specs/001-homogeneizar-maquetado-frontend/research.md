# Phase 0 Research: Homogeneizacion de Maquetado del Frontend

## Decision 1: Definir un patron base de seccion reutilizable

- Decision: Adoptar un patron comun para secciones que incluya encabezado (titulo + descripcion), area principal de contenido y fila de acciones.
- Rationale: Las listas y formularios actuales usan variaciones de estructura que dificultan orientacion y mantenimiento.
- Alternatives considered:
  - Mantener estilos por componente y ajustar caso por caso: descartado por alta variacion y deuda creciente.
  - Hacer un rediseño visual completo: descartado por fuera de alcance; la necesidad actual es consistencia de maquetado.

## Decision 2: Consolidar reglas de layout en estilos compartidos existentes

- Decision: Reforzar el uso de frontend/src/styles/{globals,utilities,components}.css y frontend/src/components/Shared.css para evitar duplicacion.
- Rationale: El proyecto ya tiene una guia de estilos y capas CSS; aprovecharla reduce riesgo y esfuerzo.
- Alternatives considered:
  - Migrar todo a CSS Modules de inmediato: descartado por impacto amplio y no necesario para homogeneizar layout.
  - Introducir una libreria externa de UI: descartado por sobrecosto y posible ruptura del look actual.

## Decision 3: Estandarizar estados de visualizacion (loading, empty, error, data)

- Decision: Definir contrato visual comun para estados de cada seccion.
- Rationale: Los estados no felices suelen romper consistencia aunque la vista principal este alineada.
- Alternatives considered:
  - Normalizar solo vistas con datos: descartado por inconsistencia residual en casos reales de uso.

## Decision 4: Validacion test-first para estructura de layout

- Decision: Incorporar pruebas frontend que fallen primero para estructura minima esperada por seccion y orden de bloques criticos.
- Rationale: La constitucion exige test-first; la consistencia visual necesita criterios automatizados, no solo inspeccion manual.
- Alternatives considered:
  - Solo checklist manual: descartado por baja repetibilidad y riesgo de regresiones silenciosas.
  - Snapshot visual masivo de toda la app: descartado por fragilidad inicial; se prefiere cobertura incremental por seccion.

## Decision 5: Mantener contratos API y backend sin cambios

- Decision: Limitar la feature a maquetado frontend, sin tocar rutas, schemas ni restricciones del scheduler.
- Rationale: El objetivo funcional es de presentacion; alterar backend agregaria riesgo innecesario.
- Alternatives considered:
  - Aprovechar para modificar payloads de componentes: descartado porque no aporta a la homogeneizacion y aumenta acoplamiento.
