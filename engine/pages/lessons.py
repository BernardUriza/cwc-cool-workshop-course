# CWC - Lessons Page

from browser import html
from ..state import get_state
from ..router import navigate
from ..config import get_config
from ..lessons.loader import get_loader


def lessons_page(params):
    state = get_state()
    config = get_config()

    container = html.DIV(Class="max-w-5xl mx-auto")

    header = html.DIV(Class="mb-8")
    header <= html.H1("📚 Lecciones", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(config.get('description') or config['tagline'], Class="text-gray-600")
    container <= header

    container <= _render_stats(state)

    loader = get_loader()
    for category in loader.get_categories():
        section = html.DIV(Class="mb-10")
        section <= html.H2(
            f"{category.get('icon', '📂')} {category['name']}",
            Class="text-xl font-semibold text-gray-700 mb-1"
        )
        if category.get('description'):
            section <= html.P(category['description'], Class="text-gray-500 text-sm mb-4")
        section <= _render_lesson_list(state, loader.get_lessons_by_category(category['id']))
        container <= section

    return container


def _render_stats(state):
    loader = get_loader()
    lessons_completed = len(state.data.get('progress', {}).get('lessons_completed', []))
    total_lessons = loader.get_lesson_count()

    stats = html.DIV(Class="grid grid-cols-3 gap-4 mb-8")

    stats <= html.DIV(
        html.SPAN(str(lessons_completed), Class="text-3xl font-bold text-indigo-600") +
        html.SPAN(f"/{total_lessons}", Class="text-xl text-gray-400") +
        html.P("Lecciones completadas", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    total_time = state.data.get('stats', {}).get('lessons', {}).get('total_time', 0)
    hours = total_time // 3600
    mins = (total_time % 3600) // 60
    stats <= html.DIV(
        html.SPAN(f"{hours}h {mins}m", Class="text-3xl font-bold text-green-600") +
        html.P("Tiempo de estudio", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    total_xp = loader.get_total_xp_available()
    stats <= html.DIV(
        html.SPAN(f"{total_xp} XP", Class="text-3xl font-bold text-amber-500") +
        html.P("XP disponible en el curso", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    return stats


def _render_lesson_list(state, lessons):
    completed = set(state.data.get('progress', {}).get('lessons_completed', []))

    grid = html.DIV(Class="grid grid-cols-1 md:grid-cols-2 gap-4")

    for i, lesson in enumerate(lessons):
        locked = i > 0 and lessons[i - 1]['id'] not in completed
        is_completed = lesson['id'] in completed

        base_classes = "bg-white rounded-xl border border-gray-100 overflow-hidden transition-all p-5"
        if locked:
            state_classes = "opacity-60"
        elif is_completed:
            state_classes = "border-green-200 bg-green-50/30"
        else:
            state_classes = "hover:shadow-md hover:border-indigo-200 cursor-pointer"

        card = html.DIV(Class=f"{base_classes} {state_classes}")

        header = html.DIV(Class="flex items-center justify-between mb-2")
        header <= html.SPAN(
            f"{lesson.get('icon', '📄')} {lesson.get('duration', 10)} min",
            Class="text-sm text-gray-500"
        )
        if is_completed:
            header <= html.SPAN("✓ Completada", Class="text-sm text-green-600")
        elif locked:
            header <= html.SPAN("🔒 Bloqueada", Class="text-sm text-gray-400")
        card <= header

        card <= html.H3(lesson.get('title', ''), Class="text-lg font-semibold text-gray-800")
        card <= html.P(lesson.get('description', '')[:120], Class="text-gray-600 mt-2 text-sm")

        footer = html.DIV(Class="flex items-center gap-4 mt-4")
        footer <= html.SPAN(
            lesson.get('difficulty', 'beginner').capitalize(),
            Class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600"
        )
        footer <= html.SPAN(
            f"⭐ {lesson.get('xp_reward', 0)} XP",
            Class="text-xs text-gray-500"
        )
        card <= footer

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
