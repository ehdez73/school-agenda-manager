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
  - [6.4.2 Restringir líneas por docente](#642-restringir-lineas-por-docente)
  - [6.4.3 Configurar horas de coordinación](#643-configurar-horas-de-coordinacion)
  - [6.5 Crear Clases Conjuntas](#65-crear-clases-conjuntas)
  - [6.6 Asignar apoyos después de generar el horario](#66-asignar-apoyos-despues-de-generar-el-horario)
- [7. Casuísticas](#7-casuisticas)
  - [7.4 Música en cursos con 3 líneas](#74-musica-en-cursos-con-3-lineas)
  - [7.5 Pack con Clase Conjunta](#75-pack-con-clase-conjunta)
  - [7.6 Horas de apoyo y coordinación: conflictos con horas no disponibles](#76-horas-de-apoyo-y-coordinacion-conflictos-con-horas-no-disponibles)
- [8. Generación del horario y revisión](#8-generacion-del-horario-y-revision)
- [9. Cómo funciona el proceso de generación](#9-como-funciona-el-proceso-de-generacion)
- [10. Restricciones: HARD y SOFT](#10-restricciones-hard-y-soft)
- [11. Problemas frecuentes y cómo resolverlos](#11-problemas-frecuentes-y-como-resolverlos)
  - [11.5 Conflicto con Clases Conjuntas](#115-conflicto-con-clases-conjuntas)
  - [11.6 Conflicto con horas de apoyo](#116-conflicto-con-horas-de-apoyo)
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
- **Asignaturas** (incluye pestañas **Packs** para agrupar asignaturas y **Clases Conjuntas** para clases compartidas entre líneas)
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

### Horas de coordinación

Tiempo no lectivo del docente dedicado a tareas de coordinación, reuniones de departamento u otras actividades organizativas. Se configuran en el formulario del docente y reducen su capacidad lectiva efectiva: si un docente tiene un máximo de 20h semanales y 2h de coordinación, el sistema solo le asignará 18h de clase. El solver coloca automáticamente estas horas de coordinación en los huecos libres del horario del docente tras la generación.

### Apoyo

Asignación manual que se realiza después de generar el horario. Permite que un docente ocupe un hueco libre apoyando a una asignatura concreta en un curso y línea determinados. Se crea haciendo clic sobre un hueco libre en el horario del docente. No interviene en el solver.

### Clase Conjunta

Mecanismo para que varias líneas (grupos) de un mismo curso compartan la misma asignatura en la misma franja horaria con el mismo docente. Existen dos modalidades:

- **Docente fijo**: se asigna un docente concreto a la Clase Conjunta.
- **Docente elegido por el solver**: el sistema elige cualquier docente cualificado, pero será el mismo para todas las líneas en cada franja.

Además, puede ser **totalmente compartida** (todas las horas semanales se imparten juntas) o **parcialmente compartida** (solo un número concreto de horas se imparten juntas; el resto son independientes por línea).

## 4. Pantalla de configuración

La pantalla de **Configuración** (menú superior) se organiza en tres pestañas.

### 4.1 Pestaña Horarios

Define la estructura temporal del centro:

- **Nº días por semana** (1-7): número de días lectivos.
- **Asignación de días**: qué día de la semana (lunes a domingo) corresponde a cada posición del horario.
- **Nº clases por día**: número de tramos horarios por día lectivo.
- **Nombres de horas**: etiquetas personalizadas para cada tramo (ej. "8:30-9:30", "Recreo", ...).
- **Bloques fijos**: tramos que se repiten todas las semanas (ej. recreo, guardias). Se muestran en el horario pero no participan en la asignación de clases. Puedes añadir, editar y eliminar bloques fijos desde esta pantalla. Cada bloque tiene:
  - **Posición**: número de orden en el horario.
  - **Etiqueta**: texto que se muestra (ej. "Recreo", "Guardia").
  - **Rango horario**: intervalo opcional (ej. "10:00-11:00").
  - **Color**: color de fondo, seleccionable con un selector de color.

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
5. Clases Conjuntas.
6. Docentes.
7. Asignación de tutoría, disponibilidad y preferencias.
8. Generación de horarios.
9. Revisión y ajustes.

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
6. Configura la cuadrícula de disponibilidad (ver [§6.4.1](#641-configurar-disponibilidad-y-preferencias)).
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

#### 6.4.2 Restringir líneas por docente

Cuando un curso tiene varias líneas (ej. 6º con A, B, C) y un docente **no** imparte todas las líneas de una asignatura, puedes restringir qué líneas concretas cubre.

Esto se configura en el mismo formulario del docente, en la sección **Restricciones de línea** que aparece cuando el docente tiene asignaturas de cursos con múltiples líneas.

Ejemplo — **Lengua (6º)** con 3 líneas:

| Docente | Asignatura | Líneas que imparte | Cómo se ve en el formulario |
|---------|------------|-------------------|-----------------------------|
| **Docente 1** | Lengua (6º) | A ✅, B ✅, C ❌ | Líneas A y B marcadas, C sin marcar |
| **Docente 2** | Lengua (6º) | A ❌, B ❌, C ✅ | Solo línea C marcada |

En este escenario:
- **Docente 1** imparte Lengua a los grupos **6ºA** y **6ºB**.
- **Docente 2** (docente de desdoble) imparte Lengua solo a **6ºC**.

Para configurarlo:

1. Abre el formulario de edición del docente.
2. Desplázate a la sección **Restricciones de línea**, debajo del selector de asignaturas.
3. Para cada asignatura, marca las líneas que el docente debe impartir y desmarca las que no.
4. Si todas las líneas están marcadas (valor por defecto), el campo `teacher_subject_lines` no se almacena, lo que significa que el docente cubre todas las líneas.
5. Guarda el formulario.

> **Qué ocurre en el planificador:**
> - Cuando al menos una línea está desmarcada, el planificador solo crea variables de asignación para las líneas marcadas.
> - Si el docente es el único cualificado para esa asignatura, asegúrate de que otro docente cubra las líneas desmarcadas; de lo contrario, el horario será inviable.
> - Un docente con `included_lines: [0, 1]` en una asignatura (como Docente 1) no se asignará a la línea C, incluso si no hay otro docente disponible; por tanto, garantiza una cobertura completa.

#### 6.4.3 Configurar horas de coordinación

El campo **Horas de coordinación** en el formulario del docente indica el tiempo semanal no lectivo dedicado a tareas organizativas (reuniones, coordinación de departamento, etc.).

1. En el formulario del docente, localiza el campo **Horas de coordinación**.
2. Introduce el número de horas semanales dedicadas a coordinación.
3. Guarda el formulario.

> **Qué ocurre en el planificador:**
> - La capacidad lectiva efectiva del docente se calcula como `max_horas_semanales - horas_coordinacion`.
> - Tras generar el horario, el sistema rellena automáticamente los huecos libres del docente con etiquetas de "Coordinación" hasta alcanzar el número configurado.
> - Las horas de coordinación se muestran en verde en el horario del docente y cuentan para el total de horas ocupadas.

### 6.5 Crear Clases Conjuntas

Las Clases Conjuntas permiten que varias líneas de un mismo curso reciban la misma asignatura a la vez, compartiendo franja horaria y docente.

1. Entra en **Asignaturas** y abre la pestaña **Clases Conjuntas**.
2. Pulsa **Añadir clase conjunta**.
3. Selecciona el **curso** (ej. 6º).
4. Selecciona la **asignatura** (ej. Música).
5. Opcional: selecciona un **docente** (si se deja vacío, el sistema elegirá automáticamente entre los cualificados).
6. Marca las **líneas** que compartirán la clase (mínimo 2).
7. Opcional: introduce un **nombre** para identificar la Clase Conjunta en el horario.
8. Opcional: define **horas compartidas** (vacío = todas las horas de la asignatura se imparten juntas).
9. Guarda.

> **Recomendaciones:**
> - Las líneas seleccionadas deben existir en el curso.
> - Si el docente se deja vacío, asegúrate de que al menos un docente cualificado pueda impartir la asignatura en todas las líneas seleccionadas.
> - Las Clases Conjuntas pueden combinarse con Packs (ver [§7.5](#75-pack-con-clase-conjunta)).

### 6.6 Asignar apoyos después de generar el horario

Los apoyos permiten que un docente ocupe un hueco libre en su horario para apoyar una asignatura concreta en otro curso o línea. Se asignan manualmente después de generar el horario.

1. Ve a **Horarios** y asegúrate de que el horario esté generado.
2. En la vista **por docente**, localiza un hueco libre (celda vacía y sin contenido).
3. Haz clic en el hueco. Se abrirá el modal **Asignar Apoyo**.
4. Selecciona la asignatura que deseas apoyar de la lista de asignaturas que se imparten en esa franja horaria.
5. Pulsa **Asignar Apoyo**.

Para eliminar un apoyo existente, haz clic sobre la etiqueta de apoyo (aparece con el color de la asignatura y la etiqueta "APOYO") y pulsa **Eliminar Apoyo**.

> **Qué ocurre en el planificador:**
> - El solver no interviene en los apoyos. Se asignan siempre después de la generación.
> - Las horas de apoyo cuentan para el total de horas ocupadas del docente.
> - No se puede asignar un apoyo en una franja que el docente haya marcado como **No disponible** (rojo). Si se intenta, el sistema muestra un error.
> - Si un docente tenía un apoyo en una franja que posteriormente se marca como No disponible, el apoyo existente se muestra con un icono de advertencia ⚠️ en el horario.
> - Tampoco se puede asignar un apoyo en una franja donde el docente ya tenga clase o coordinación.

## 7. Casuísticas

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

### 7.4 Música en cursos con 3 líneas

Objetivo: que dos líneas compartan la clase de Música mientras la tercera es independiente. Es el caso más habitual cuando un curso tiene 3 líneas (A, B, C) y el centro solo puede atender 2 grupos simultáneos de Música.

Cómo configurarlo:

1. Crea la asignatura Música para el curso (ej. MUS6 para 6º).
2. Crea una Clase Conjunta (pestaña **Clases Conjuntas** en Asignaturas).
3. Selecciona el curso (6º), la asignatura (Música).
4. Marca las líneas **B y C**.
5. Selecciona un docente (o déjalo vacío para que el solver elija).
6. Deja **horas compartidas** vacío (= todas las horas).
7. Guarda.

Resultado esperado:

- **6ºA** recibe Música de forma independiente en sus propias franjas.
- **6ºB y 6ºC** reciben Música juntos en la misma franja, con el mismo docente.
- El horario refleja que 6ºB y 6ºC comparten la clase (aparece como "Música (Conjunta)" o el nombre asignado).
- Las horas semanales de Música (2h) se asignan correctamente a cada línea.

### 7.5 Pack con Clase Conjunta

Objetivo: combinar un Pack (Religión / Atención Educativa) con una Clase Conjunta para Religión, de modo que un curso de 3 líneas (A, B, C) ofrezca Religión a las tres líneas pero Atención Educativa solo en A y B, mientras que Religión se imparte conjuntamente para B y C.

Cómo configurarlo:

1. Crea la asignatura **Religión (6º)** (REL6) y la asignatura **Atención Educativa (6º)** (ATE6).
2. Marca en ATE6 que solo aplica a las líneas **A y B** (desmarca línea C).
3. Crea un Pack **RELAT6** que incluya REL6 y ATE6.
4. Crea una **Clase Conjunta** para REL6 con las líneas **B y C**, horas compartidas vacío (todas las horas).
5. Opcional: asigna un docente a la Clase Conjunta, o déjalo vacío para que el solver elija.

Resultado esperado:

- **6ºA**: tiene ambas opciones (REL6 y ATE6) en el Pack RELAT6. No participa en la Clase Conjunta.
- **6ºB**: tiene ambas opciones (REL6 y ATE6) en el Pack RELAT6. Además, REL6 está en la Clase Conjunta B/C, por lo que cuando se cursa Religión lo hace junto con 6ºC.
- **6ºC**: cursa Religión (no tiene ATE6, solo líneas A y B). Lo hace junto con 6ºB gracias a la Clase Conjunta.
- El solver asigna la misma franja a REL6 y ATE6 en las líneas A y B (por el Pack), y además sincroniza REL6 entre B y C (por la Clase Conjunta).
- En el horario, la franja de REL6 aparece como "Religión (Conjunta)" para 6ºB y 6ºC.

> **Nota importante:** cuando un Pack y una Clase Conjunta afectan a la misma asignatura, el sistema resuelve ambas restricciones simultáneamente. Asegúrate de que las líneas de la Clase Conjunta y las del Pack sean coherentes para evitar conflictos.

### 7.6 Horas de apoyo y coordinación: conflictos con horas no disponibles

Este caso muestra qué ocurre cuando las horas no disponibles de un docente entran en conflicto con los distintos tipos de horas de apoyo.

**Escenario 1 — Clase asignada por el solver + hora no disponible**

El docente marca el lunes 3ª hora como **No disponible** (rojo). El solver nunca asignará una clase en esa franja gracias a la restricción HARD `TeacherUnavailableTimes`. Si todas las franjas disponibles del docente están marcadas como No disponible, el solver no encontrará una solución y se activará el diagnóstico de infactibilidad.

**Escenario 2 — Apoyo manual + hora no disponible**

El docente tiene un apoyo asignado manualmente en una franja que posteriormente marca como **No disponible**. En este caso:
- El apoyo existente **no** se elimina automáticamente.
- En el horario del docente, la celda muestra un icono de advertencia ⚠️ junto a la etiqueta de apoyo.
- El sistema sigue mostrando el apoyo pero señaliza visualmente el conflicto.
- Para resolverlo, el usuario debe eliminar manualmente el apoyo (clic en la etiqueta → **Eliminar Apoyo**) o desmarcar la franja como No disponible.
- Si se intenta crear un apoyo nuevo en una franja No disponible, el sistema lo rechaza con un error.

**Escenario 3 — Coordinación + hora no disponible**

Las horas de coordinación se asignan automáticamente por el sistema después de la generación **únicamente** en huecos libres que no sean No disponible. Por tanto, nunca hay conflicto entre coordinación y horas no disponibles.

## 8. Generación del horario y revisión

1. Ve a **Horarios**.
2. Pulsa **Generar Horario**. El proceso puede tardar unos segundos.
3. Espera a la finalización del proceso.
4. El horario se muestra en dos secciones: **por curso** y **por docente**.
   - Usa los filtros de búsqueda y los selectores de la parte superior para elegir qué cursos o docentes ver.
   - El panel lateral permite navegar rápidamente entre grupos o docentes.
   - Activa o desactiva **Mostrar filas fijas** para incluir u ocultar recreos u otros bloques fijos.
5. Puedes **Descargar Markdown** para guardar el horario en un archivo, o **Imprimir** para obtener una vista para papel.
6. En la vista **por curso** o **por docente**, haz clic sobre cualquier **bloque fijo** (recreo, guardia, etc.) para editar su texto en ese día y grupo o docente concreto. Se abre un modal que permite:
   - **Guardar** un texto personalizado.
   - **Restaurar el valor por defecto** de la configuración.
   - **Limpiar** el texto (dejarlo vacío).
7. Si hace falta, corrige datos y vuelve a generar.

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
|:---|:---|:---|:---|
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
| HARD | **JointClassAssignment** | Asegura que las líneas de una Clase Conjunta compartan la misma franja y, si hay docente fijo, también el mismo docente. | Música 6º B/C → 6ºB y 6ºC tienen Música a la vez. |
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

### Error 11.5: conflicto con Clases Conjuntas

Revisa:

- Que la Clase Conjunta tenga al menos 2 líneas seleccionadas.
- Que las horas compartidas no superen las horas semanales de la asignatura.
- Que el docente asignado (si es fijo) esté cualificado para impartir la asignatura.
- Que las líneas de la Clase Conjunta sean coherentes con las líneas del Pack si se combinan ambos (ver [§7.5](#75-pack-con-clase-conjunta)).
- Que ningún docente tenga una sobrecarga horaria por estar asignado a múltiples Clases Conjuntas.

### Error 11.6: conflicto con horas de apoyo

Revisa:

- Que el docente no tenga la franja marcada como **No disponible** (rojo) al asignar un apoyo.
- Si ves una advertencia ⚠️ en el horario del docente, elimina el apoyo existente o desmarca la franja como No disponible.
- Que las horas de coordinación configuradas no superen el máximo semanal del docente (la capacidad efectiva se reduce automáticamente).
- Que los apoyos asignados no hagan que el docente supere su cómputo total de horas.

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
  - [ ] Clases Conjuntas configuradas (Música, Religión, EF, etc.).
- [ ] Todos los docentes con asignaturas.
- [ ] Máximos semanales revisados.
- [ ] Disponibilidades cargadas correctamente.
- [ ] Horas de coordinación configuradas donde corresponda.
- [ ] Tutorías asignadas.

Si todo el checklist está completo, genera el horario.
