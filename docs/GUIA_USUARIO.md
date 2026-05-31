# Guia de Usuario - School Agenda Manager

Guia orientada a Jefatura de Estudios para administrar la aplicacion: crear estructura academica, configurar profesorado y generar horarios.

Esta guia es funcional y de uso diario. No incluye aspectos tecnicos.

## Indice

Nota: este indice esta pensado para usarse como navegacion rapida en el panel lateral de tu visor Markdown.

- [1. Objetivo de la aplicacion](#1-objetivo-de-la-aplicacion)
- [2. Mapa rapido de secciones](#2-mapa-rapido-de-secciones)
- [3. Definiciones clave](#3-definiciones-clave)
- [4. Orden recomendado de trabajo](#4-orden-recomendado-de-trabajo)
- [5. Como crear cada elemento](#5-como-crear-cada-elemento)
- [6. Casuisticas de Packs](#6-casuisticas-de-packs)
- [7. Generacion del horario y revision](#7-generacion-del-horario-y-revision)
- [8. Restricciones: HARD y SOFT](#8-restricciones-hard-y-soft)
- [9. Problemas frecuentes y como resolverlos](#9-problemas-frecuentes-y-como-resolverlos)
- [10. Buenas practicas de gestion](#10-buenas-practicas-de-gestion)
- [11. Checklist final antes de generar](#11-checklist-final-antes-de-generar)

## 1. Objetivo de la aplicacion

La aplicacion permite construir y mantener los horarios del centro de forma centralizada, respetando:

- La carga semanal de cada asignatura.
- La disponibilidad y limites del profesorado.
- La coherencia por curso y linea.
- Las reglas de Packs y preferencias de planificacion.

## 2. Mapa rapido de secciones

En el menu superior, la gestion habitual se organiza en:

- Cursos
- Asignaturas
- Packs
- Docentes
- Horarios
- Configuracion

## 3. Definiciones clave

### Curso

Nivel educativo (por ejemplo, 1º, 2º, I3, I4, I5).

### Linea o Clase

Subdivision de un curso (A, B, etc.).
Ejemplo: 1ºA y 1ºB son dos lineas del curso 1º.

### Asignatura

Materia impartida en un curso con una carga de horas semanales.
Ejemplo: Lengua 1º, Matematicas 3º, Musica I4A.

### Pack

Conjunto de asignaturas que se gestionan de forma coordinada en el horario.
En esta guia, Pack equivale a Grupo de Asignaturas.

### shared_hours (horas compartidas en un Pack)

Numero de horas semanales en las que las asignaturas del Pack deben coincidir en la misma franja.

### Docente

Profesor o profesora que imparte una o varias asignaturas, con limite maximo semanal.

### Tutor

Docente asignado a uno o varios grupos de tutoria.

### Disponibilidad

Franjas donde el docente no puede impartir clase.

### Preferencias

Franjas deseadas para priorizar la ubicacion de clases al generar horario.

## 4. Orden recomendado de trabajo

Para evitar errores y retrabajo, sigue siempre este orden:

1. Configuracion general (dias, horas por dia, tramos horarios).
2. Cursos (y numero de lineas).
3. Asignaturas.
4. Packs.
5. Docentes.
6. Asignacion de tutoria, disponibilidad y preferencias.
7. Generacion de horarios.
8. Revision y ajustes.

## 5. Como crear cada elemento

### 5.1 Crear cursos

1. Entra en Cursos.
2. Crea cada curso con su nombre.
3. Define el numero de lineas (A, B, etc.).

Recomendaciones:

- Revisa que todas las lineas reales del centro esten creadas.
- Si un curso tiene dos grupos, indica 2 lineas desde el inicio.

### 5.2 Crear asignaturas

1. Entra en Asignaturas.
2. Crea cada asignatura indicando curso y horas semanales.
3. Completa opciones si aplican (maximo por dia, impartir todos los dias, horas consecutivas, etc.).

Recomendaciones:

- Verifica que cada asignatura tenga una carga semanal correcta.
- Evita duplicados con nombres similares.

### 5.3 Crear Packs

1. Entra en la pestana Packs dentro de Asignaturas.
2. Crea el Pack con nombre identificable.
3. Selecciona las asignaturas que lo forman.
4. Si corresponde, define shared_hours.
5. Guarda.

Validaciones utiles:

- Las asignaturas de un Pack deben estar bien definidas antes.
- Si usas shared_hours, su valor debe ser coherente con las horas semanales de las asignaturas del Pack.

### 5.4 Crear docentes

1. Entra en Docentes.
2. Crea cada docente con nombre.
3. Asigna asignaturas que puede impartir.
4. Define maximo de horas semanales.
5. Asigna grupo tutor cuando corresponda.

Recomendaciones:

- Ninguna asignatura debe quedarse sin docentes asignados.
- Ajusta maximos semanales realistas para evitar bloqueos en la generacion.

### 5.5 Configurar disponibilidad y preferencias

1. Entra al docente.
2. Marca tramos no disponibles.
3. Marca tramos preferidos.
4. Guarda.

Criterio practico:

- Usa no disponible solo cuando sea obligatorio.
- Usa preferencia para orientar el resultado sin bloquear en exceso.

## 6. Casuisticas de Packs

### 6.1 Caso Religion / Atencion Educativa

Objetivo: que ambas opciones se gestionen como bloque coordinado.

Como configurarlo:

1. Crea Asignatura Religion del curso correspondiente.
2. Crea Asignatura Atencion Educativa del mismo curso.
3. Crea un Pack (por ejemplo, RELAT1 para 1º).
4. Incluye ambas asignaturas en ese Pack.
5. Guarda y revisa que el Pack aparece asociado a las dos.

Resultado esperado:

- El horario trata esta combinacion como Pack.
- Se mantiene la coherencia de franjas para este caso.

### 6.2 Caso Comunicacion y representacion de la realidad / Musica

Objetivo: modelar el caso especifico de Infantil con horas compartidas.

Como configurarlo:

1. Crea la asignatura Comunicacion y representacion de la realidad del nivel correspondiente.
2. Crea la asignatura Musica del mismo nivel.
3. Crea un Pack por grupo/nivel (ejemplo: COMUI3A, COMUI4A, COMUI5A).
4. Añade ambas asignaturas al Pack.
5. Define shared_hours = 1.
6. Guarda y verifica.

Resultado esperado:

- El Pack existe con shared_hours = 1.
- El horario fuerza la coincidencia en 1 hora compartida semanal para ese Pack.

### 6.3 Diferencia entre Pack sin shared_hours y Pack con shared_hours

- Pack sin shared_hours: relaciona asignaturas del Pack sin forzar una cantidad explicita de horas compartidas.
- Pack con shared_hours: obliga a compartir exactamente el numero de horas indicado.

## 7. Generacion del horario y revision

1. Ve a Horarios.
2. Pulsa Generar Horario.
3. Espera a la finalizacion del proceso.
4. Revisa por curso y por docente.
5. Si hace falta, corrige datos y vuelve a generar.

Cuando usar Recrear Horarios:

- Tras cambios importantes en cursos, packs o disponibilidades.

## 8. Restricciones: HARD y SOFT

En Configuracion > Restricciones veras dos bloques:

- Restricciones obligatorias (HARD).
- Restricciones opcionales o de preferencia (SOFT).

### Diferencia entre HARD y SOFT

- HARD: definen condiciones que el horario debe cumplir para ser valido. Si no se pueden satisfacer, normalmente no se genera un horario valido.
- SOFT: no invalidan el horario si no se cumplen al 100%. Se usan para mejorar la calidad del resultado (menos huecos, mejor ajuste a preferencias, etc.).

Ejemplo rapido:

- HARD: Un docente no puede estar en dos clases a la misma hora.
- SOFT: Intentar poner al docente en sus horas preferidas.

### Tabla de restricciones

| Tipo | Restriccion | Para que sirve | Ejemplo |
| --- | --- | --- | --- |
| HARD | Horas semanales de la asignatura (SubjectWeeklyHours) | Garantiza que cada asignatura cumpla sus horas semanales por grupo. | Matematicas 1º con 5 horas debe aparecer exactamente 5 horas. |
| HARD | Un docente por clase a la vez (TeacherOneClassAtATime) | Evita que un docente imparta dos clases en la misma franja. | El docente de Ingles no puede estar a la vez en 2ºA y 2ºB a las 10:00. |
| HARD | Franjas no disponibles del docente (TeacherUnavailableTimes) | Bloquea horas marcadas como no disponibles. | Si una docente no esta disponible los martes a 5ª hora, no se le asignara clase en esa franja. |
| HARD | Max. horas semanales del docente (TeacherMaxWeeklyHours) | Respeta el maximo semanal configurado para cada docente. | Con maximo 23 horas, no se asignaran 24 o mas. |
| HARD | Max. horas/dia de la asignatura por grupo (GroupSubjectMaxHoursPerDay) | Limita cuantas veces puede repetirse una asignatura el mismo dia en un grupo. | Si Lengua tiene maximo 2 al dia, no puede salir 3 veces el martes en 3ºA. |
| HARD | Una asignatura logica por hora y grupo (GroupAtMostOneLogicalAssignment) | Asegura que un grupo tenga solo una asignatura (o Pack) por franja. | 1ºA no puede tener simultaneamente Matematicas y Ciencias a 3ª hora. |
| HARD | Un unico docente por asignatura en cada franja (GroupSubjectAtMostOneTeacherPerTimeslot) | Evita asignar dos docentes a la misma asignatura del mismo grupo en la misma franja. | Musica de 4ºA a 2ª hora no puede tener dos docentes a la vez. |
| HARD | Horas consecutivas de asignatura por grupo (GroupSubjectHoursMustBeConsecutive) | Si una asignatura marcada como consecutiva aparece varias veces el mismo dia, debe ir en bloque continuo. | Si EF en 5ºA tiene 2 horas el jueves, deben ser 4ª-5ª, no 2ª y 5ª. |
| HARD | Horas NO consecutivas de asignatura por grupo (GroupSubjectHoursMustNotBeConsecutive) | En asignaturas marcadas como no consecutivas, separa las horas del mismo dia. | Lengua en 2ºB con 2 horas el lunes no puede ir 2ª-3ª seguidas. |
| HARD | Asignaturas vinculadas consecutivas (LinkedSubjectsConsecutive) | Cuando dos asignaturas estan vinculadas, deben ir en horas contiguas cuando coinciden el mismo dia. | Laboratorio vinculado a Ciencias debe colocarse justo antes o justo despues. |
| HARD | Asignacion de pack de asignaturas (SubjectGroupAssignment) | Obliga a que las asignaturas del Pack se asignen en la misma franja. | Religion y Atencion Educativa dentro de RELAT1 deben compartirse en la franja definida para el Pack. |
| HARD | Asignatura debe impartirse cada dia (SubjectMustEveryDay) | Para asignaturas marcadas con esta opcion, exige al menos una hora diaria. | Si una asignatura de lectura esta marcada como diaria, debe aparecer de lunes a viernes. |
| SOFT | Horas obligatorias del tutor (TutorMandatoryHours) | Favorece que el tutor este asignado en primera y ultima hora de la semana para su grupo. | Prioriza que el tutor de 1ºA tenga clase con 1ºA al inicio y cierre de semana. |
| SOFT | Franjas preferidas del docente (TeacherPreferredTimes) | Prioriza colocar clases en horas preferidas por cada docente. | Si un docente marca preferencia por primera mitad de la manana, el sistema intentara ubicar ahi sus clases. |
| SOFT | Preferencia del tutor (TutorPreference) | Favorece que los tutores impartan clase en su grupo tutorizado. | Prioriza que la tutora de 3ºB imparta mas horas en 3ºB que en otros grupos. |
| SOFT | Evitar huecos del profesorado (TeacherAvoidGaps) | Penaliza horarios con huecos entre clases, buscando bloques mas compactos. | Mejor 2ª-3ª-4ª seguidas que 2ª y 5ª con huecos intermedios. |

## 9. Problemas frecuentes y como resolverlos

### Error 1: no se puede generar horario valido

Revisa:

- Asignaturas sin docente.
- Docentes con maximo semanal demasiado bajo.
- Demasiadas indisponibilidades.
- Packs mal definidos o shared_hours incoherente.

### Error 2: una asignatura no aparece con las horas esperadas

Revisa:

- Horas semanales de la asignatura.
- Si pertenece a Pack y tiene horas condicionadas.
- Si esta restringida por maximo por dia o por reglas de consecutividad.

### Error 3: sobrecarga de un docente

Revisa:

- Maximo semanal del docente.
- Reparto de asignaturas entre mas docentes.
- Disponibilidad excesivamente limitada.

### Error 4: conflicto en grupos de tutoria

Revisa:

- Asignacion de tutorias en Docentes.
- Que el mismo docente no acumule tutorias imposibles de cubrir.

## 10. Buenas practicas de gestion

- Mantener nomenclatura consistente para cursos, asignaturas y packs.
- Crear primero estructura academica y luego profesorado.
- Aplicar shared_hours solo cuando exista una necesidad real.
- Evitar usar restricciones muy duras en demasiados docentes a la vez.
- Regenerar el horario despues de cada bloque de cambios relevantes.

## 11. Checklist final antes de generar

- Configuracion general revisada.
- Cursos y lineas completos.
- Todas las asignaturas creadas con horas correctas.
- Packs creados y validados.
- Casos especiales configurados:
  - Religion / Atencion Educativa.
  - Comunicacion y representacion de la realidad / Musica con shared_hours=1 cuando aplique.
- Todos los docentes con asignaturas.
- Maximos semanales revisados.
- Disponibilidades cargadas correctamente.
- Tutorias asignadas.

Si todo el checklist esta correcto, genera el horario.
