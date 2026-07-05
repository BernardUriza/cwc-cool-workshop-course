# PromptCraft - Lesson Detail Page
# Página de detalle de lección

from browser import document, html, timer
from ..state import get_state
from ..router import navigate
from ..components.button import Button
from ..components.code_editor import CodeEditor, PromptEditor
from ..components.progress import ProgressBar
from ..components.modal import SuccessModal
from ..components.toast import success, xp_toast
from ..gamification.xp import award_xp
from ..gamification.achievements import check_achievements


def lesson_detail_page(params):
    """
    Renderiza la página de detalle de una lección.

    Args:
        params: Diccionario con 'id' de la lección

    Returns:
        Elemento DOM de la página
    """
    lesson_id = params.get('id', '')
    lesson = _get_lesson_data(lesson_id)

    if not lesson:
        return _render_not_found(lesson_id)

    state = get_state()
    is_completed = lesson_id in state.data.get('lessons_completed', [])

    container = html.DIV(Class="max-w-4xl mx-auto")

    # Breadcrumb
    breadcrumb = html.DIV(Class="mb-6")
    breadcrumb <= html.A("← Volver a Lecciones", href="#lessons", Class="text-indigo-600 hover:text-indigo-800")
    container <= breadcrumb

    # Header
    header = _render_header(lesson, is_completed)
    container <= header

    # Contenido de la lección
    content = _render_content(lesson)
    container <= content

    # Ejercicio interactivo
    if lesson.get('exercise'):
        exercise = _render_exercise(lesson, state)
        container <= exercise

    # Navegación de lección
    nav = _render_lesson_nav(lesson_id)
    container <= nav

    # Botón de completar
    if not is_completed:
        complete_btn = _render_complete_button(lesson_id, state)
        container <= complete_btn

    return container


def _render_not_found(lesson_id):
    """Renderiza página de lección no encontrada."""
    return html.DIV(
        html.SPAN("📚", Class="text-6xl text-gray-300") +
        html.H1(f"Lección '{lesson_id}' no encontrada", Class="text-xl font-bold text-gray-700 mt-4") +
        html.A("← Volver a Lecciones", href="#lessons", Class="mt-4 text-indigo-600 hover:text-indigo-800"),
        Class="text-center py-16"
    )


def _render_header(lesson, is_completed):
    """Renderiza el header de la lección."""
    header = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100 mb-6")

    # Badge de completado
    if is_completed:
        header <= html.DIV(
            html.SPAN("✓ Completada", Class="text-green-600 font-medium"),
            Class="mb-4"
        )

    # Título
    header <= html.H1(lesson.get('title', 'Lección'), Class="text-2xl font-bold text-gray-800 mb-2")

    # Descripción
    header <= html.P(lesson.get('description', ''), Class="text-gray-600 mb-4")

    # Metadata
    meta = html.DIV(Class="flex items-center gap-4 text-sm")

    # Categoría
    cat_icon = {'fundamentos': '📚', 'tecnicas': '🎯', 'avanzado': '🚀', 'casos': '💼'}
    cat = lesson.get('category', 'fundamentos')
    meta <= html.SPAN(
        f"{cat_icon.get(cat, '📖')} {cat.capitalize()}",
        Class="text-gray-500"
    )

    # Dificultad
    diff_colors = {'beginner': 'text-green-600', 'intermediate': 'text-yellow-600', 'advanced': 'text-red-600'}
    diff_labels = {'beginner': 'Principiante', 'intermediate': 'Intermedio', 'advanced': 'Avanzado'}
    diff = lesson.get('difficulty', 'beginner')
    meta <= html.SPAN(
        diff_labels.get(diff, diff),
        Class=f"font-medium {diff_colors.get(diff, 'text-gray-600')}"
    )

    # Duración
    meta <= html.SPAN(f"⏱️ {lesson.get('duration', '10 min')}", Class="text-gray-500")

    # XP
    meta <= html.SPAN(f"+{lesson.get('xp', 50)} XP", Class="text-indigo-600 font-medium")

    header <= meta

    return header


def _render_content(lesson):
    """Renderiza el contenido de la lección."""
    content = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100 mb-6")

    sections = lesson.get('sections', [])

    for section in sections:
        section_elem = html.DIV(Class="mb-8 last:mb-0")

        # Título de sección
        if section.get('title'):
            section_elem <= html.H2(section['title'], Class="text-xl font-semibold text-gray-800 mb-4")

        # Contenido según tipo
        section_type = section.get('type', 'text')

        if section_type == 'text':
            for para in section.get('paragraphs', []):
                section_elem <= html.P(para, Class="text-gray-600 mb-3 leading-relaxed")

        elif section_type == 'example':
            example_block = html.DIV(Class="bg-gray-50 rounded-lg p-4 border-l-4 border-indigo-500")
            example_block <= html.P("💡 Ejemplo", Class="font-medium text-indigo-700 mb-2")
            example_block <= html.DIV(
                html.PRE(section.get('prompt', ''), Class="text-sm text-gray-700 whitespace-pre-wrap"),
                Class="bg-gray-800 text-gray-100 p-3 rounded font-mono text-sm mb-2"
            )
            if section.get('output'):
                example_block <= html.DIV(
                    html.P("Resultado:", Class="text-sm text-gray-500 mb-1") +
                    html.P(section['output'], Class="text-gray-700 italic"),
                    Class="mt-3"
                )
            section_elem <= example_block

        elif section_type == 'tip':
            tip_block = html.DIV(Class="bg-amber-50 rounded-lg p-4 border-l-4 border-amber-500")
            tip_block <= html.P("💡 Consejo", Class="font-medium text-amber-700 mb-2")
            tip_block <= html.P(section.get('content', ''), Class="text-amber-800")
            section_elem <= tip_block

        elif section_type == 'warning':
            warn_block = html.DIV(Class="bg-red-50 rounded-lg p-4 border-l-4 border-red-500")
            warn_block <= html.P("⚠️ Advertencia", Class="font-medium text-red-700 mb-2")
            warn_block <= html.P(section.get('content', ''), Class="text-red-800")
            section_elem <= warn_block

        elif section_type == 'list':
            list_elem = html.UL(Class="list-disc list-inside space-y-2")
            for item in section.get('items', []):
                list_elem <= html.LI(item, Class="text-gray-600")
            section_elem <= list_elem

        content <= section_elem

    # Contenido por defecto si no hay secciones
    if not sections:
        content <= html.P(
            "El contenido de esta lección estará disponible pronto.",
            Class="text-gray-500 italic text-center py-8"
        )

    return content


def _render_exercise(lesson, state):
    """Renderiza el ejercicio interactivo."""
    exercise = lesson.get('exercise', {})

    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100 mb-6")
    section <= html.H2("🎯 Ejercicio Práctico", Class="text-xl font-semibold text-gray-800 mb-4")
    section <= html.P(exercise.get('instruction', 'Practica lo aprendido.'), Class="text-gray-600 mb-4")

    # Editor de prompt
    editor = PromptEditor(
        value=exercise.get('starter_code', ''),
        placeholder="Escribe tu prompt aquí...",
        variables=exercise.get('variables', {}),
        template_mode=exercise.get('use_variables', False),
        show_run_button=True,
        on_run=lambda code: _on_run_exercise(code, exercise, section)
    )
    section <= editor.render()

    # Área de resultado
    section <= html.DIV(
        html.P("El resultado aparecerá aquí...", Class="text-gray-400 italic"),
        Class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200",
        id="exercise-result"
    )

    return section


def _on_run_exercise(code, exercise, container):
    """Ejecuta el ejercicio (simulado)."""
    result_elem = document.getElementById("exercise-result")
    if not result_elem:
        return

    result_elem.innerHTML = ""
    result_elem <= html.P("⏳ Procesando...", Class="text-gray-500")

    # Simular delay
    def show_result():
        result_elem.innerHTML = ""

        # Verificar si el código cumple con los requisitos
        requirements = exercise.get('requirements', [])
        passed = all(req.lower() in code.lower() for req in requirements)

        if passed:
            result_elem.className = "mt-4 p-4 bg-green-50 rounded-lg border border-green-200"
            result_elem <= html.P("✅ ¡Excelente! Tu prompt cumple con los requisitos.", Class="text-green-700 font-medium")
            result_elem <= html.P(
                exercise.get('success_message', 'Has completado el ejercicio correctamente.'),
                Class="text-green-600 mt-2"
            )
        else:
            result_elem.className = "mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200"
            result_elem <= html.P("💡 Casi lo tienes, pero hay algo que puedes mejorar.", Class="text-yellow-700 font-medium")
            result_elem <= html.P(
                exercise.get('hint', 'Revisa los conceptos de la lección e intenta de nuevo.'),
                Class="text-yellow-600 mt-2"
            )

    timer.set_timeout(show_result, 1000)


def _render_lesson_nav(current_id):
    """Renderiza navegación entre lecciones."""
    nav = html.DIV(Class="flex justify-between items-center py-4")

    # Botón anterior
    nav <= html.BUTTON(
        "← Anterior",
        Class="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
    )

    # Indicador de progreso
    nav <= html.SPAN("Lección 3 de 20", Class="text-sm text-gray-500")

    # Botón siguiente
    nav <= html.BUTTON(
        "Siguiente →",
        Class="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
    )

    return nav


def _render_complete_button(lesson_id, state):
    """Renderiza botón de completar lección."""
    wrapper = html.DIV(Class="text-center py-6")

    btn = html.BUTTON(
        "✓ Marcar como Completada",
        Class="px-8 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
    )

    def on_complete(e):
        # Marcar como completada
        if 'lessons_completed' not in state.data:
            state.data['lessons_completed'] = []

        if lesson_id not in state.data['lessons_completed']:
            state.data['lessons_completed'].append(lesson_id)
            state.save()

            # Otorgar XP
            award_xp(state, 'lesson_complete', reason=f"Lección completada")

            # Verificar achievements
            check_achievements(state, 'lesson_complete', {'lesson_id': lesson_id})

            # Mostrar modal de éxito
            modal = SuccessModal(
                title="¡Lección Completada!",
                message="Has terminado esta lección exitosamente.",
                xp_gained=50
            )
            modal.show()

            # Actualizar botón
            btn.innerHTML = "✓ Completada"
            btn.className = "px-8 py-3 bg-gray-400 text-white font-medium rounded-lg cursor-not-allowed"
            btn.disabled = True

    btn.bind('click', on_complete)
    wrapper <= btn

    return wrapper


def _get_lesson_data(lesson_id):
    """
    Obtiene los datos de una lección.
    En producción, esto cargaría de un archivo JSON.
    """
    # Datos de ejemplo
    lessons_data = {
        'intro-prompting': {
            'id': 'intro-prompting',
            'title': 'Introducción al Prompting',
            'description': 'Aprende qué es un prompt y cómo funciona la comunicación con modelos de IA.',
            'category': 'fundamentos',
            'difficulty': 'beginner',
            'duration': '10 min',
            'xp': 50,
            'sections': [
                {
                    'title': '¿Qué es un Prompt?',
                    'type': 'text',
                    'paragraphs': [
                        'Un prompt es el texto o instrucción que le das a un modelo de inteligencia artificial para obtener una respuesta. Es la forma en que te comunicas con la IA.',
                        'La calidad del prompt determina en gran medida la calidad de la respuesta. Un prompt bien estructurado puede hacer la diferencia entre una respuesta mediocre y una excelente.',
                    ]
                },
                {
                    'type': 'example',
                    'prompt': '¿Cuál es la capital de Francia?',
                    'output': 'La capital de Francia es París.'
                },
                {
                    'title': 'Componentes de un Buen Prompt',
                    'type': 'list',
                    'items': [
                        'Claridad: El prompt debe ser claro y sin ambigüedades.',
                        'Contexto: Proporciona información relevante.',
                        'Especificidad: Sé específico sobre lo que esperas.',
                        'Formato: Indica cómo quieres la respuesta.',
                    ]
                },
                {
                    'type': 'tip',
                    'content': 'Piensa en el prompt como una conversación. Cuanto más claro seas, mejor te entenderá la IA.'
                }
            ],
            'exercise': {
                'instruction': 'Escribe un prompt para obtener una receta de pasta.',
                'starter_code': 'Dame una receta de pasta',
                'requirements': ['receta', 'pasta'],
                'success_message': '¡Bien hecho! Ahora intenta ser más específico sobre el tipo de pasta.',
                'hint': 'Incluye las palabras "receta" y "pasta" en tu prompt.'
            }
        }
    }

    return lessons_data.get(lesson_id)
