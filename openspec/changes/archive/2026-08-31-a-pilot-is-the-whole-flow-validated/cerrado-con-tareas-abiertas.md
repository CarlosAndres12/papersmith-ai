# Cerrado con tareas abiertas — a-pilot-is-the-whole-flow-validated

**Cerrado:** 2026-09-14 · **Última actividad real:** 2026-08-31 · **Tareas:** 22 hechas, 5 abiertas.

## Por qué se cierra con cinco tareas sin marcar

Las cinco viven bajo un encabezado que lo dice de sí mismo: *"Phase 3:
Cross-cutting — explicitly out of scope this session (not assigned)"*. Nunca
fueron trabajo asignado de este cambio; eran el borde que el cambio decidió no
cruzar. Tres de las cuatro sustantivas ya están hechas, en otra parte:

- **3.2 (emparejar con `\b`)** — hecho. `tests/forge_vocabulary.py:241`,
  `leak_pattern(word)` devuelve `re.compile(rf"\b{re.escape(word)}s?\b")`, y su
  docstring escribe la razón: `arm` solo dispara sobre `warm`, `harm` y `alarm`.
  Aterrizó el 2026-09-04 en `16593dd`, cuatro días DESPUÉS de la última
  actividad real de este cambio. `test_proposal_implementation.py` y
  `test_skill_audit.py` importan de ahí en vez de volver a deletrearlo.
- **3.3 / 3.4 (la regla B se deriva del disco)** — hecho, y antes de que la
  tarea se escribiera. `tests/test_proposal_implementation.py:12071`,
  `target_words()` recorre `implementations/*/src/*` en vivo, y
  `derived_denylist()` (`:12130`) hace `skipTest` en voz alta cuando no hay
  target, en lugar de pasar en silencio — *"una guarda que pasa porque no tuvo
  nada que mirar se lee igual que una guarda que miró y no encontró nada"*.
  Aterrizó el 2026-08-20 en `5602818`.
- **3.5** es una corrida de verificación, no trabajo.

## El residuo que sí queda

**3.1 no está hecha.** Ninguna prueba negativa afirma que una palabra que
meramente CONTIENE una palabra del piso no se reporta como fuga. El
comportamiento es correcto — el patrón está anclado y las dos clases que lo usan
lo documentan —, pero el escenario que la especificación de este cambio pide
sigue sin sostén: las fixtures plantadas (`PLANTED`, `:6541`) siempre plantan la
palabra exacta, nunca una que la contenga. Lo que falta es la prueba, no la
conducta. Queda escrito acá para que nadie lo redescubra desde cero ni lo
reporte como si fuera un defecto nuevo.

## Qué NO significa

No significa que las cinco tareas se hayan declarado innecesarias. Significa que
cuatro dejaron de ser deuda — tres porque ya están, una porque nunca fue trabajo
— y que la quinta, 3.1, es deuda de prueba, no de comportamiento. Si alguien
quiere cerrarla, se escribe contra el estado actual del piso de vocabulario,
nunca contra la Fase 3 de este documento, que ya no describe el repositorio.
