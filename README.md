# cwc-cool-workshop-course

Template para cursos y workshops interactivos: Brython (Python en el browser) +
Tailwind + KaTeX, sin backend, deployable en GitHub Pages con un fork.

Derivado de [promptcraft-brython](https://github.com/BernardUriza/promptcraft-brython-)
con la arquitectura de contenido de [The Carpentries Workbench](https://carpentries.github.io/workbench/):
**el contenido y el motor viven separados**.

## Qué trae

- **Lecciones** con anatomía Carpentries: `questions` (preguntas guía) →
  `objectives` → cuerpo con secciones tipadas (text/tip/warning/example/code) →
  `keypoints`
- **Retrieval practice**: quiz de repaso que muestrea 1 pregunta de lo último
  cubierto + 2 de cobertura media + 2 de lo más viejo (patrón de
  [retrievalpractice.org](https://pdf.retrievalpractice.org/SpacingGuide.pdf))
- **Gamificación completa**: XP, niveles, badges, achievements y rachas diarias
- **Puzzles** de lógica, **práctica** con editor, **assessment** diagnóstico y
  **proyecto final**
- **KaTeX vendoreado** (sin CDN): fórmulas con `$$ ... $$` (bloque) o `\( ... \)`
  (inline) en cualquier contenido
- Persistencia en localStorage, aislada por curso (`course.json → id`)

## Crear tu curso

Todo lo que se edita vive en `content/`. El motor (`engine/`) no se toca.

1. **Fork** este repo (o úsalo como template en GitHub)
2. Edita `content/course.json`: `id` (único, aísla el progreso), `name`, `logo`,
   `tagline`, `footer` y qué `features` van encendidas
3. Escribe tus lecciones en `content/lessons/<id>.json` y regístralas en
   `content/lessons/index.json` (categorías + orden)
4. Alimenta el banco de quizzes en `content/quizzes.json` (llave = id de lección)
5. Ajusta `content/assessment.json`, `content/practice.json` y
   `content/puzzles/` si usas esas features
6. GitHub Pages: Settings → Pages → deploy from branch `main` / root

## Desarrollo local

```bash
python3 -m http.server 8000
open http://localhost:8000
```

Brython importa `engine/` vía el server — abrir `index.html` con `file://` no
funciona; siempre usa un server local.

## Estructura

```
├── index.html            ← entry point (Brython 3.14.3 + KaTeX)
├── content/              ← TODO lo editable del curso
│   ├── course.json       ← branding, features on/off
│   ├── lessons/          ← index.json + una lección por JSON
│   ├── quizzes.json      ← banco de retrieval por lección
│   ├── assessment.json   ← test diagnóstico
│   ├── practice.json     ← ejercicios de práctica
│   └── puzzles/          ← index.json + un puzzle por JSON
├── engine/               ← el motor (no se edita para crear un curso)
│   ├── app.py, router.py, state.py, config.py
│   ├── components/       ← UI reutilizable
│   ├── gamification/     ← XP, niveles, badges, rachas
│   ├── lessons/          ← loader + renderer
│   ├── retrieval/        ← sampler del quiz 1+2+2
│   └── pages/            ← páginas de la SPA
└── vendor/katex/         ← KaTeX self-hosted
```
