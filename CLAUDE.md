# cwc-cool-workshop-course — Boot

Template genérico multi-curso: Brython SPA + Tailwind + KaTeX, sin backend,
GitHub Pages. Derivado de promptcraft-brython con arquitectura Carpentries
(contenido y motor separados).

## Regla de oro

**El contenido vive en `content/`, el motor en `engine/`.** Crear o modificar un
curso = editar JSON en `content/`. Si una feature de curso te obliga a tocar
`engine/`, es un cambio de TEMPLATE (beneficia a todos los cursos) y se hace
genérico, nunca hardcodeado a un curso concreto. Contenido embebido en Python es
el smell que motivó este template — no reintroducirlo.

## Verificación (Art. 2)

- `python3 -m py_compile engine/*.py engine/**/*.py` tras cualquier edición
- `python3 -m http.server 8000` + Chrome: el boot real es la única prueba —
  Brython truena en runtime cosas que compilan bien
- E2E mínimo tras cambios al motor: home → lección → completar (XP debe subir
  en `progress.xp`) → quiz → calificar (XP mostrado == XP sumado)

## Gotchas aprendidas (2026-07-05)

- El XP vive en `state.data['progress']['xp']` — el bug original escribía a
  `state.data['xp']` que nadie lee
- `renderMath()` reintenta solo (KaTeX carga con defer); llamarlo tras montar
  contenido con fórmulas: `timer.set_timeout(lambda: window.renderMath('app'), 200)`
- El storage key es `cwc_state::<course.json id>` — cursos distintos en el mismo
  origin (GitHub Pages del mismo usuario) no colisionan
- Math inline en JSON: `\\(...\\)`; display: `$$...$$`
- El sampler de retrieval deduplica por (lesson_id, question) — solo pregunta
  sobre lecciones completadas
- `difficulty` en content es string (easy/medium/hard); el engine la normaliza a
  1-5 en `puzzles/loader.normalize_puzzle` — esa es LA frontera, no agregar
  mapeos ad-hoc en componentes

## Deuda conocida

- `get_all_lessons()` hace N XHRs síncronos secuenciales (uno por lección). Con
  ~30+ lecciones el home/lecciones se sentirá lento en Pages; la cura es un
  build step que agregue `content/lessons/all.json` o migrar el loader a
  async+callback como el de puzzles.
