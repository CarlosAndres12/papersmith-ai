# Cerrado con tareas abiertas — the-skill-materializes-not-the-agent

**Cerrado:** 2026-09-14 · **Última actividad real:** 2026-08-30 · **Tareas:** 67 hechas, 5 abiertas.

## Lo primero: no corras 2.5.1–2.5.3

Esas tres tareas mandan adoptar, una por una, los **11 destinos de scaffold** de
`implementations/Domain_Adaptation`. Esa migración nunca corrió: no existe
ningún `materialization.json` en ninguna parte bajo `implementations/`, medido
hoy. Y correrla ahora haría daño real.

El cambio en curso, `the-comparison-nobody-asked-for`, **mueve dos de esos
once**: `src/<Package>_Benchmark/__init__.py` deja de ser destino de scaffold y
pasa a ser el cuarto destino de la etapa `harness` — se escribe solo después de
una comparación aceptada —, y el módulo de sellado deja de existir en esa ruta,
porque se reubica como `src/<Package>/report_digest.py`. Su especificación lo
exige explícitamente: `materialize --adopt` registra cada destino *"scoped to
the stage list it actually belongs to (scaffold or harness)"*. Adoptar los once
de hoy grabaría dos asientos de recibo contra la etapa equivocada, que es
exactamente lo que esa especificación prohíbe — y el recibo es lo que después se
lee para decidir si un archivo derivó o nunca pasó por el motor.

La migración que estas tres tareas pedían es hoy un subconjunto propio del
requisito de migración del cambio en curso, que además sabe adónde va cada
archivo. Se cierra acá para que se haga una sola vez, allá, y bien.

## Las otras dos: 4.4 y 4.5

Piden **borrar** `scripts/materialize.py`. **Decisión tomada, 2026-09-14: el
archivo se queda.** El operador falló a favor de la reescritura que diseña el
cambio en curso (§D9): los tres sitios imperativos de ese archivo se reemplazan
por un bucle sobre las propias listas del motor — `scaffold_destinations(name)`,
`scaffold_kit_source(...)`, `authored_package_init(name)` —, de modo que la
deriva se vuelve imposible en vez de detectable. No es una disputa abierta; es
una decisión registrada.

Borrarlo más adelante sigue siendo posible, y la reescritura lo abarata: la
tarea 4.4 ya admitía por escrito que la eliminación era *"materially larger and
riskier than this task's one-line framing suggests"*, justamente por los tres
sitios imperativos. Con un solo bucle, eso deja de ser cierto.

## Dónde están los artefactos de planificación

Esta carpeta solo tiene `tasks.md`, y eso no es un fragmento: los artefactos de
planificación de este cambio nunca se escribieron a disco, solo se espejó
`tasks.md`. Viven completos en Engram, bajo
`sdd/the-skill-materializes-not-the-agent/` — observaciones **#1254**
(`explore`), **#1258** (`proposal`), **#1262** (`spec`), **#1266** (`design`),
**#1272** (`tasks`) y **#1278** (`apply-progress`), todas del 2026-08-30. No se
borró ni se perdió nada.

## Qué NO significa

No significa que las cinco tareas estén hechas. Tres se cierran porque
ejecutarlas hoy causaría daño y su trabajo lo absorbió el cambio en curso; dos
se cierran porque el operador falló en contra de lo que pedían. Ninguna es un
pendiente que alguien deba retomar desde este documento: la vara vigente es
`the-comparison-nobody-asked-for`, no la Fase 2.5 ni la Fase 4 de acá.
