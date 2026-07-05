# PromptCraft - Lessons Page
# Página de lista de lecciones

from browser import document, html
from ..state import get_state
from ..router import navigate


def lessons_page(params):
    """
    Renderiza la página de lecciones.

    Args:
        params: Parámetros de la ruta

    Returns:
        Elemento DOM de la página
    """
    state = get_state()

    container = html.DIV(Class="max-w-5xl mx-auto")

    # Header
    header = html.DIV(Class="mb-8")
    header <= html.H1("📚 Lecciones", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(
        "Aprende las técnicas fundamentales y avanzadas de Prompt Engineering.",
        Class="text-gray-600"
    )
    container <= header

    # Estadísticas rápidas
    stats = _render_stats(state)
    container <= stats

    # Tabs por categoría
    tabs_content = _render_lessons_tabs(state)
    container <= tabs_content

    return container


def _render_stats(state):
    """Renderiza estadísticas de lecciones."""
    lessons_completed = len(state.data.get('progress', {}).get('lessons_completed', []))
    total_lessons = 20

    stats = html.DIV(Class="grid grid-cols-3 gap-4 mb-8")

    # Completadas
    stats <= html.DIV(
        html.SPAN(str(lessons_completed), Class="text-3xl font-bold text-indigo-600") +
        html.SPAN(f"/{total_lessons}", Class="text-xl text-gray-400") +
        html.P("Lecciones completadas", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    # Tiempo total
    total_time = state.data.get('stats', {}).get('lessons', {}).get('total_time', 0)
    hours = total_time // 3600
    mins = (total_time % 3600) // 60

    stats <= html.DIV(
        html.SPAN(f"{hours}h {mins}m", Class="text-3xl font-bold text-green-600") +
        html.P("Tiempo de estudio", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    # Siguiente desbloqueo
    stats <= html.DIV(
        html.SPAN("🔓", Class="text-3xl") +
        html.P("3 lecciones más", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    return stats


def _render_lessons_tabs(state):
    """Renderiza lista de lecciones (versión simplificada)."""
    # Simplificado - mostrar todas las lecciones directamente
    return _render_lesson_list(state, 'all')


def _render_lesson_list(state, category):
    """Renderiza lista de lecciones de una categoría."""
    lessons = _get_lessons(category)
    completed = set(state.data.get('progress', {}).get('lessons_completed', []))

    grid = html.DIV(Class="grid grid-cols-1 md:grid-cols-2 gap-4")

    for i, lesson in enumerate(lessons):
        # Determinar si está bloqueada
        locked = False
        if i > 0:
            prev_lesson = lessons[i - 1]
            if prev_lesson['id'] not in completed:
                locked = True

        is_completed = lesson['id'] in completed

        # Card simplificada sin usar LessonCard
        base_classes = "bg-white rounded-xl border border-gray-100 overflow-hidden transition-all p-5"
        if locked:
            state_classes = "opacity-60"
        elif is_completed:
            state_classes = "border-green-200 bg-green-50/30"
        else:
            state_classes = "hover:shadow-md hover:border-indigo-200 cursor-pointer"

        card = html.DIV(Class=f"{base_classes} {state_classes}")

        # Header
        header = html.DIV(Class="flex items-center justify-between mb-2")
        header <= html.SPAN(lesson.get('category', '').capitalize(), Class="text-sm text-gray-500")
        if is_completed:
            header <= html.SPAN("✓ Completada", Class="text-sm text-green-600")
        elif locked:
            header <= html.SPAN("🔒 Bloqueada", Class="text-sm text-gray-400")
        card <= header

        # Title & description
        card <= html.H3(lesson.get('title', ''), Class="text-lg font-semibold text-gray-800")
        card <= html.P(lesson.get('description', '')[:100], Class="text-gray-600 mt-2 text-sm")

        # Footer
        footer = html.DIV(Class="flex items-center gap-4 mt-4")
        footer <= html.SPAN(lesson.get('difficulty', 'beginner').capitalize(), Class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600")
        footer <= html.SPAN(f"⏱️ {lesson.get('duration', '10 min')}", Class="text-xs text-gray-500")
        card <= footer

        # Click handler
        if not locked:
            lesson_id = lesson['id']
            card.bind('click', lambda e, lid=lesson_id: navigate('lesson/:id', {'id': lid}))

        grid <= card

    if not lessons:
        grid <= html.DIV(
            html.SPAN("📭", Class="text-4xl text-gray-300") +
            html.P("No hay lecciones en esta categoría aún.", Class="text-gray-400 mt-2"),
            Class="col-span-full text-center py-12"
        )

    return grid


def _get_lessons(category='all'):
    """
    Obtiene lecciones (placeholder - en producción vendría de JSON).
    """
    all_lessons = [
        # Fundamentos
        {
            'id': 'intro-prompting',
            'title': 'Introducción al Prompting',
            'description': 'Aprende qué es un prompt y cómo funciona la comunicación con modelos de IA.',
            'category': 'fundamentos',
            'difficulty': 'beginner',
            'duration': '10 min',
        },
        {
            'id': 'anatomia-prompt',
            'title': 'Anatomía de un Prompt',
            'description': 'Descubre las partes que componen un prompt efectivo.',
            'category': 'fundamentos',
            'difficulty': 'beginner',
            'duration': '15 min',
        },
        {
            'id': 'claridad-especificidad',
            'title': 'Claridad y Especificidad',
            'description': 'Cómo ser claro y específico para obtener mejores resultados.',
            'category': 'fundamentos',
            'difficulty': 'beginner',
            'duration': '12 min',
        },
        {
            'id': 'contexto-efectivo',
            'title': 'Contexto Efectivo',
            'description': 'La importancia del contexto y cómo proporcionarlo.',
            'category': 'fundamentos',
            'difficulty': 'beginner',
            'duration': '15 min',
        },

        # Técnicas
        {
            'id': 'zero-shot',
            'title': 'Zero-Shot Prompting',
            'description': 'Obtén resultados sin proporcionar ejemplos previos.',
            'category': 'tecnicas',
            'difficulty': 'intermediate',
            'duration': '15 min',
        },
        {
            'id': 'few-shot',
            'title': 'Few-Shot Prompting',
            'description': 'Usa ejemplos para guiar el comportamiento del modelo.',
            'category': 'tecnicas',
            'difficulty': 'intermediate',
            'duration': '20 min',
        },
        {
            'id': 'chain-of-thought',
            'title': 'Chain of Thought',
            'description': 'Guía al modelo a razonar paso a paso.',
            'category': 'tecnicas',
            'difficulty': 'intermediate',
            'duration': '20 min',
        },
        {
            'id': 'role-playing',
            'title': 'Role-Playing',
            'description': 'Asigna roles y personalidades al modelo.',
            'category': 'tecnicas',
            'difficulty': 'intermediate',
            'duration': '15 min',
        },
        {
            'id': 'self-consistency',
            'title': 'Self-Consistency',
            'description': 'Múltiples caminos de razonamiento para mejores resultados.',
            'category': 'tecnicas',
            'difficulty': 'intermediate',
            'duration': '18 min',
        },

        # Avanzado
        {
            'id': 'tree-of-thoughts',
            'title': 'Tree of Thoughts',
            'description': 'Exploración ramificada de soluciones.',
            'category': 'avanzado',
            'difficulty': 'advanced',
            'duration': '25 min',
        },
        {
            'id': 'react-pattern',
            'title': 'ReAct Pattern',
            'description': 'Razonamiento y acción combinados.',
            'category': 'avanzado',
            'difficulty': 'advanced',
            'duration': '25 min',
        },
        {
            'id': 'prompt-chaining',
            'title': 'Prompt Chaining',
            'description': 'Encadena múltiples prompts para tareas complejas.',
            'category': 'avanzado',
            'difficulty': 'advanced',
            'duration': '30 min',
        },

        # Casos de Uso
        {
            'id': 'code-generation',
            'title': 'Generación de Código',
            'description': 'Prompts efectivos para programación.',
            'category': 'casos',
            'difficulty': 'intermediate',
            'duration': '20 min',
        },
        {
            'id': 'content-writing',
            'title': 'Escritura de Contenido',
            'description': 'Crea contenido de alta calidad con IA.',
            'category': 'casos',
            'difficulty': 'beginner',
            'duration': '15 min',
        },
        {
            'id': 'data-analysis',
            'title': 'Análisis de Datos',
            'description': 'Usa IA para analizar y visualizar datos.',
            'category': 'casos',
            'difficulty': 'intermediate',
            'duration': '20 min',
        },
    ]

    if category == 'all':
        return all_lessons

    return [l for l in all_lessons if l.get('category') == category]
