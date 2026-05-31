# Guía de Usuario

Guía orientada a Jefatura de Estudios para administrar la aplicación: crear estructura académica, configurar profesorado y generar horarios.

Esta guía es funcional y de uso diario. No incluye aspectos técnicos.

## Índice

Nota: este índice está pensado para usarse como navegación rápida en el panel lateral de tu visor Markdown.

- [1. Objetivo de la aplicación](#1-objetivo-de-la-aplicacion)
- [2. Mapa rápido de secciones](#2-mapa-rapido-de-secciones)
- [3. Definiciones clave](#3-definiciones-clave)
- [4. Pantalla de configuración](#4-pantalla-de-configuracion)
- [5. Orden recomendado de trabajo](#5-orden-recomendado-de-trabajo)
- [6. Cómo crear cada elemento](#6-como-crear-cada-elemento)
- [7. Casuísticas de Packs](#7-casuisticas-de-packs)
- [8. Generación del horario y revisión](#8-generacion-del-horario-y-revision)
- [9. Cómo funciona el proceso de generación](#9-como-funciona-el-proceso-de-generacion)
- [10. Restricciones: HARD y SOFT](#10-restricciones-hard-y-soft)
- [11. Problemas frecuentes y cómo resolverlos](#11-problemas-frecuentes-y-como-resolverlos)
- [12. Buenas prácticas de gestión](#12-buenas-practicas-de-gestion)
- [13. Checklist final antes de generar](#13-checklist-final-antes-de-generar)

## 1. Objetivo de la aplicación

La aplicación permite construir y mantener los horarios del centro de forma centralizada, respetando:

- La carga semanal de cada asignatura.
- La disponibilidad y límites del profesorado.
- La coherencia por curso y línea.
- Las reglas de Packs y preferencias de planificación.

## 2. Mapa rápido de secciones

En el menú superior, la gestión habitual se organiza en:

- **Cursos**
- **Asignaturas** (incluye una pestaña **Packs** para agrupar asignaturas)
- **Docentes**
- **Horarios**
- **Configuración**
- **Ayuda**

## 3. Definiciones clave

### Curso

Nivel educativo (por ejemplo, 1º, 2º, I3, I4, I5).

### Línea o Clase

Subdivisión de un curso (A, B, etc.).
Ejemplo: 1ºA y 1ºB son dos líneas del curso 1º.

### Asignatura

Materia impartida en un curso con una carga de horas semanales.
Ejemplo: Lengua 1º, Matemáticas 3º, Música I4A.

### Pack

Conjunto de asignaturas que se gestionan de forma coordinada en el horario.
En esta guía, Pack equivale a Grupo de Asignaturas.

### Horas compartidas

Número de horas semanales en las que las asignaturas del Pack deben coincidir en la misma franja.
- Si no se indica un número (vacío = "Todas las horas"), **todas las horas** del Pack se imparten juntas.
- Si se indica un número concreto, solo esas horas son compartidas; el resto son independientes por asignatura.

### Docente

Profesor o profesora que imparte una o varias asignaturas, con límite máximo semanal.

### Tutor

Docente asignado a uno o varios grupos de tutoría.

### Cuadrícula de disponibilidad

Cuadrícula donde se configuran las franjas no disponibles y preferidas del docente para la generación del horario.

### Preferencias

Franjas deseadas para priorizar la ubicación de clases al generar horario.

## 4. Pantalla de configuración

La pantalla de **Configuración** (menú superior) se organiza en tres pestañas.

### 4.1 Pestaña Horarios

Define la estructura temporal del centro:

- **Nº días por semana** (1-7): número de días lectivos.
- **Asignación de días**: qué día de la semana (lunes a domingo) corresponde a cada posición del horario.
- **Nº clases por día**: número de tramos horarios por día lectivo.
- **Nombres de horas**: etiquetas personalizadas para cada tramo (ej. "8:30-9:30", "Recreo", ...).
- **Bloques fijos**: tramos que se repiten todas las semanas (ej. recreo, guardias). Se muestran en el horario pero no participan en la asignación de clases.

Guarda siempre los cambios con el botón **Guardar**.

### 4.2 Pestaña Restricciones

Permite activar o desactivar restricciones individuales. Consulta la [sección 10](#10-restricciones-hard-y-soft) para una definición detallada de cada una.

- **Restricciones obligatorias (HARD)**: condiciones que el horario debe cumplir para ser válido. Desactivar una puede facilitar la generación, pero el resultado podría ser pedagógicamente inválido.
- **Restricciones opcionales (SOFT)**: preferencias que mejoran la calidad del horario pero no bloquean la generación si no se cumplen.

Todas las restricciones están activadas por defecto. Desmarca una casilla para desactivarla.

### 4.3 Pestaña Copia de seguridad

Gestiona los datos completos de la aplicación (cursos, asignaturas, packs, docentes, horarios):

- **Exportar**: descarga un archivo `agenda_export.json` con todos los datos.
- **Importar**: selecciona un archivo JSON previamente exportado para restaurar los datos.
- **Limpiar datos**: elimina todos los datos de la aplicación. Requiere confirmación.

> **Recomendación:** exporta los datos antes de hacer cambios estructurales importantes.

## 5. Orden recomendado de trabajo

Para evitar errores y retrabajo, sigue siempre este orden:

1. Configuración general (días, horas por día, tramos horarios).
2. Cursos (y número de líneas).
3. Asignaturas.
4. Packs.
5. Docentes.
6. Asignación de tutoría, disponibilidad y preferencias.
7. Generación de horarios.
8. Revisión y ajustes.

## 6. Cómo crear cada elemento

### 6.1 Crear cursos

1. Entra en Cursos.
2. Crea cada curso con su nombre.
3. Define el número de líneas (A, B, etc.).

> **Recomendaciones:**
> - Revisa que todas las líneas reales del centro estén creadas.
> - Si un curso tiene dos grupos, indica 2 líneas desde el inicio.

### 6.2 Crear asignaturas

1. Entra en **Asignaturas**.
2. Crea cada asignatura con nombre, curso, color y horas semanales.
3. Si el curso tiene varias líneas, puedes **desmarcar líneas concretas** para excluir la asignatura de esas líneas.
4. Completa opciones si aplican (máximo por día, horas consecutivas, impartir todos los días, asignatura vinculada, etc.).

> **Recomendaciones:**
> - Verifica que cada asignatura tenga una carga semanal correcta.
> - Evita duplicados con nombres similares.
> - Si una asignatura solo se imparte en algunas líneas, usa los checkboxes de línea para excluir las que no correspondan.

### 6.3 Crear Packs

1. Entra en la pestaña **Packs** dentro de Asignaturas.
2. Crea el Pack con nombre identificable.
3. Selecciona las asignaturas que lo forman.
4. Si corresponde, define las horas compartidas.
5. Guarda.

> **Validaciones útiles:**
> - Las asignaturas de un Pack deben estar bien definidas antes.
> - Si usas horas compartidas, su valor debe ser coherente con las horas semanales de las asignaturas del Pack.

### 6.4 Crear docentes

1. Entra en Docentes.
2. Crea cada docente con nombre.
3. Asigna asignaturas que puede impartir.
4. Define máximo de horas semanales.
5. Asigna grupo tutor cuando corresponda.
6. Configura la cuadrícula de disponibilidad (más abajo).
7. Si el docente es coordinador, asígnale las horas que usará para coordinación.

> **Recomendaciones:**
> - Ninguna asignatura debe quedarse sin docentes asignados.
> - Ajusta máximos semanales realistas para evitar bloqueos en la generación.

#### 6.4.1 Configurar disponibilidad y preferencias

Cada celda de la cuadrícula (día × hora) es un botón que alterna entre tres estados al hacer clic:

1. **Sin preferencia** (gris/neutro) — el docente puede o no tener clase en esa franja.
2. **No disponible** (rojo) — el docente no puede impartir clase en esa franja. El sistema no asignará clases aquí.
3. **Preferida** (verde) — el docente prefiere tener clase en esa franja. El sistema intentará priorizarla.

Cada clic avanza al siguiente estado: `Sin preferencia → No disponible → Preferida → Sin preferencia → ...`

> **Criterio práctico:**
> - Usa **No disponible** solo cuando sea obligatorio (médico, guardia, otro centro).
> - Usa **Preferida** para orientar el resultado sin bloquear en exceso.
> - Los cambios se guardan junto con el resto del formulario del docente.

## 7. Casuísticas de Packs

### 7.1 Caso Religión / Atención Educativa

Objetivo: que ambas opciones se gestionen como bloque coordinado.

Cómo configurarlo:

1. Crea Asignatura Religión del curso correspondiente.
2. Crea Asignatura Atención Educativa del mismo curso.
3. Crea un Pack (por ejemplo, RELAT1 para 1º).
4. Incluye ambas asignaturas en ese Pack.
5. Guarda y revisa que el Pack aparece asociado a las dos.

Resultado esperado:

- El horario trata esta combinación como Pack.
- Se mantiene la coherencia de franjas para este caso.

### 7.2 Caso Comunicación y representación de la realidad / Música

Objetivo: modelar el caso específico de Infantil con horas compartidas.

Cómo configurarlo:

1. Crea la asignatura Comunicación y representación de la realidad del nivel correspondiente.
2. Crea la asignatura Música del mismo nivel.
3. Crea un Pack por grupo/nivel (ejemplo: COMUI3A, COMUI4A, COMUI5A).
4. Añade ambas asignaturas al Pack.
5. Define horas compartidas = 1.
6. Guarda y verifica.

Resultado esperado:

- El Pack existe con horas compartidas = 1.
- El horario fuerza la coincidencia en 1 hora compartida semanal para ese Pack.

### 7.3 Diferencia entre Pack sin horas compartidas y Pack con horas compartidas

- Pack **sin** horas compartidas (vacío = "Todas las horas"): **todas las horas** de las asignaturas del Pack se imparten juntas en la misma franja.
- Pack **con** horas compartidas (valor concreto): solo ese número de horas se imparte conjuntamente; el resto de horas son independientes por asignatura.

## 8. Generación del horario y revisión

1. Ve a **Horarios**.
2. Pulsa **Generar Horario**. El proceso puede tardar unos segundos.
3. Espera a la finalización del proceso.
4. El horario se muestra en dos secciones: **por curso** y **por docente**.
   - Usa los filtros de búsqueda y los selectores de la parte superior para elegir qué cursos o docentes ver.
   - El panel lateral permite navegar rápidamente entre grupos o docentes.
   - Activa o desactiva **Mostrar filas fijas** para incluir u ocultar recreos u otros bloques fijos.
5. Puedes **Descargar Markdown** para guardar el horario en un archivo, o **Imprimir** para obtener una vista para papel.
6. Si hace falta, corrige datos y vuelve a generar.

> **Cuándo usar Recrear Horarios:**
> - Tras cambios importantes en cursos, packs o disponibilidades.
> - Recrear Horarios elimina el horario actual y genera uno nuevo desde cero.

## 9. Cómo funciona el proceso de generación

### 9.1 Generar un horario

Cuando pulsas **Generar Horario**, el sistema utiliza Google OR-Tools, un motor de optimización, para buscar una combinación válida de asignaciones de clases que cumpla con todas las restricciones configuradas.

### 9.2 Fases del proceso

La generación pasa por hasta dos fases:

**Fase 1 — Búsqueda de solución**  
El solver intenta encontrar un horario válido que cumpla con todas las restricciones HARD. Si lo consigue, el horario se muestra inmediatamente.

**Fase 2 — Diagnóstico de infactibilidad (solo si la Fase 1 falla)**  
Si el solver no encuentra una solución válida, se inicia automáticamente un proceso de diagnóstico en varios pasos:

1. **Comprobaciones de sanidad** — Validación rápida del modelo de datos (ej. cada asignatura tiene un docente, las horas totales son coherentes).
2. **Pruebas de aislamiento** — El sistema elimina restricciones temporalmente una a una para identificar cuál causa el conflicto.
3. **Análisis por entidad** — Para cada restricción conflictiva, identifica los cursos, docentes o asignaturas específicos implicados.

El resultado es un informe de diagnóstico que describe exactamente qué impide generar el horario y qué cambios se recomiendan.

### 9.3 ¿Por qué puede tardar tanto?

La generación de horarios es un problema de **explosión combinatoria**. Piensa en un centro pequeño:

- 6 cursos × 2 líneas = 12 grupos
- 10 asignaturas por grupo
- 5 días × 6 horas = 30 franjas semanales
- 15 docentes

Cada clase (grupo + asignatura) debe colocarse en una de las franjas disponibles, respetando todas las restricciones a la vez. El número de combinaciones posibles es astronómicamente grande — mucho mayor que el número de átomos en el universo.

OR-Tools utiliza una técnica llamada **CP-SAT** (Programación con Restricciones — Satisfacibilidad) para navegar este espacio de búsqueda de forma inteligente:

- Aplica **propagación de restricciones**: cuando una variable toma un valor, elimina inmediatamente todos los valores de otras variables que violarían alguna restricción.
- Usa **heurísticas** para decidir qué variable probar a continuación y qué valor asignar primero.
- Puede **retroceder** cuando llega a un punto muerto y probar caminos alternativos.
- Para las restricciones SOFT, utiliza una **función objetivo** para maximizar la calidad global de la solución.

A pesar de estas optimizaciones, algunas configuraciones pueden tardar más:

- **Restricciones muy ajustadas** (muchos docentes con indisponibilidades que se solapan).
- **Gran número de grupos y asignaturas** (más variables y combinaciones).
- **Packs u horas compartidas conflictivas** que reducen el espacio de búsqueda pero aumentan la complejidad de cada comprobación.

En la mayoría de los casos reales, el solver encuentra una solución en segundos o un par de minutos. Si tarda demasiado, considera revisar tus restricciones o simplificar la configuración.

## 10. Restricciones: HARD y SOFT

Ve a **Configuración** y haz clic en la pestaña **Restricciones**. Allí verás dos bloques:

- Restricciones obligatorias (HARD).
- Restricciones opcionales o de preferencia (SOFT).

### Diferencia entre HARD y SOFT

- HARD: definen condiciones que el horario debe cumplir para ser válido. Si no se pueden satisfacer, normalmente no se genera un horario válido.
- SOFT: no invalidan el horario si no se cumplen al 100%. Se usan para mejorar la calidad del resultado (menos huecos, mejor ajuste a preferencias, etc.).

Ejemplo rápido:

- HARD: Un docente no puede estar en dos clases a la misma hora.
- SOFT: Intentar poner al docente en sus horas preferidas.

### Tabla de restricciones

| Tipo | Restricción | Para qué sirve | Ejemplo |
| --- | --- | --- | --- |
| HARD | **SubjectWeeklyHours** | Garantiza que cada asignatura cumpla sus horas semanales por grupo. | Matemáticas 1º con 5h → aparece exactamente 5h. |
| HARD | **TeacherOneClassAtATime** | Evita que un docente tenga dos clases en la misma franja. | El docente de Inglés no puede estar en 2ºA y 2ºB a las 10:00. |
| HARD | **TeacherUnavailableTimes** | Bloquea horas marcadas como no disponibles. | Martes 5ª hora marcado → no se asigna clase ahí. |
| HARD | **TeacherMaxWeeklyHours** | Respeta el máximo semanal de cada docente. | Máx. 23h → no se asignan 24h. |
| HARD | **GroupSubjectMaxHoursPerDay** | Limita las veces que una asignatura se repite en un día en un grupo. | Lengua máx. 2/día → no puede salir 3 veces el martes en 3ºA. |
| HARD | **GroupAtMostOneLogicalAssignment** | Un grupo solo puede tener una asignatura (o Pack) por franja. | 1ºA no puede tener Matemáticas y Ciencias a la vez a 3ª hora. |
| HARD | **GroupSubjectAtMostOneTeacherPerTimeslot** | Una misma asignatura y grupo no puede tener dos docentes en la misma franja. | Música 4ºA a 2ª hora → un solo docente. |
| HARD | **GroupSubjectHoursMustBeConsecutive** | Asignaturas con "Horas consecutivas": las horas del mismo día deben formar un bloque contiguo. | EF 5ºA con 2h el jueves → deben ser 4ª-5ª, no 2ª y 5ª. |
| HARD | **GroupSubjectHoursMustNotBeConsecutive** | Asignaturas SIN "Horas consecutivas": las horas del mismo día no pueden ser adyacentes. | Lengua 2ºB con 2h el lunes → no pueden ser 2ª-3ª. |
| HARD | **LinkedSubjectsConsecutive** | Asignaturas vinculadas: cuando coinciden el mismo día, van en horas contiguas. | Laboratorio vinculado a Ciencias → justo antes o después. |
| HARD | **SubjectGroupAssignment** | Todas las asignaturas de un Pack se asignan a la misma franja. | Religión y A. Educativa en RELAT1 → misma franja. |
| HARD | **SubjectMustEveryDay** | Asignaturas marcadas como "Impartir todos los días": al menos una hora diaria. | Lectura diaria → aparece lunes a viernes. |
| SOFT | **TutorMandatoryHours** | Favorece que el tutor esté en primera y última hora de la semana con su grupo. | Tutor de 1ºA priorizado al inicio y cierre de semana. |
| SOFT | **TeacherPreferredTimes** | Prioriza colocar clases en las franjas preferidas del docente. | Docente prefiere mañana → el sistema lo intenta. |
| SOFT | **TutorPreference** | Favorece que los tutores impartan clase en su grupo tutorizado. | Tutora de 3ºB → más horas en 3ºB que en otros grupos. |
| SOFT | **TeacherAvoidGaps** | Penaliza huecos entre clases, buscando bloques más compactos. | Mejor 2ª-3ª-4ª seguidas que 2ª y 5ª con huecos. |

## 11. Problemas frecuentes y cómo resolverlos

### Error 11.1: no se puede generar horario válido

Revisa:

- Asignaturas sin docente.
- Docentes con máximo semanal demasiado bajo.
- Demasiadas indisponibilidades.
- Packs mal definidos o horas compartidas incoherentes.

### Error 11.2: una asignatura no aparece con las horas esperadas

Revisa:

- Horas semanales de la asignatura.
- Si pertenece a Pack y tiene horas condicionadas.
- Si está restringida por máximo por día o por reglas de consecutividad.

### Error 11.3: sobrecarga de un docente

Revisa:

- Máximo semanal del docente.
- Reparto de asignaturas entre más docentes.
- Disponibilidad excesivamente limitada.

### Error 11.4: conflicto en grupos de tutoría

Revisa:

- Asignación de tutorías en Docentes.
- Que el mismo docente no acumule tutorías imposibles de cubrir.

## 12. Buenas prácticas de gestión

- Mantener nomenclatura consistente para cursos, asignaturas y packs.
- Crear primero estructura académica y luego profesorado.
- Aplicar horas compartidas solo cuando exista una necesidad real.
- Evitar usar restricciones muy duras en demasiados docentes a la vez.
- Regenerar el horario después de cada bloque de cambios relevantes.

## 13. Checklist final antes de generar

- [ ] Configuración general revisada.
- [ ] Cursos y líneas completos.
- [ ] Todas las asignaturas creadas con horas correctas.
- [ ] Packs creados y validados.
- [ ] Casos especiales configurados:
  - [ ] Religión / Atención Educativa.
  - [ ] Comunicación y representación de la realidad / Música con horas compartidas=1 cuando aplique.
- [ ] Todos los docentes con asignaturas.
- [ ] Máximos semanales revisados.
- [ ] Disponibilidades cargadas correctamente.
- [ ] Tutorías asignadas.

Si todo el checklist está completo, genera el horario.
