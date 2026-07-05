# CWC - Lesson Detail Page

from browser import html, window, timer
from ..state import get_state
from ..router import navigate
from ..components.modal import SuccessModal
from ..gamification.xp import award_xp
from ..gamification.achievements import check_achievements
from ..lessons.loader import get_loader
from ..lessons.renderer import LessonRenderer


def lesson_detail_page(params):
    lesson_id = params.get('id', '')
    loader = get_loader()
    lesson = loader.get_lesson(lesson_id)

    if not lesson:
        return _render_not_found(lesson_id)

    state = get_state()
    completed = state.data.get('progress', {}).get('lessons_completed', [])
    is_completed = lesson_id in completed

    container = html.DIV(Class="max-w-4xl mx-auto")

    breadcrumb = html.DIV(Class="mb-6")
    breadcrumb <= html.A(
        "← Volver a Lecciones", href="#lessons",
        Class="text-indigo-600 hover:text-indigo-800"
    )
    container <= breadcrumb

    if is_completed:
        container <= html.DIV(
            html.SPAN("✓ Ya completaste esta lección", Class="text-green-600 font-medium"),
            Class="mb-4"
        )

    container <= LessonRenderer(lesson).render()

    container <= _render_lesson_nav(loader, lesson)

    if not is_completed:
        container <= _render_complete_button(lesson, state)

    timer.set_timeout(lambda: window.renderMath('app'), 200)

    return container


def _render_not_found(lesson_id):
    return html.DIV(
        html.SPAN("📚", Class="text-6xl text-gray-300") +
        html.H1(f"Lección '{lesson_id}' no encontrada", Class="text-xl font-bold text-gray-700 mt-4") +
        html.A("← Volver a Lecciones", href="#lessons", Class="mt-4 text-indigo-600 hover:text-indigo-800"),
        Class="text-center py-16"
    )


def _render_lesson_nav(loader, lesson):
    nav = html.DIV(Class="flex justify-between items-center py-4")

    prev_lesson = loader.get_previous_lesson(lesson['id'])
    next_lesson = loader.get_next_lesson(lesson['id'])

    if prev_lesson:
        prev_btn = html.BUTTON(
            f"← {prev_lesson['title']}",
            Class="px-4 py-2 text-gray-600 hover:text-gray-800"
        )
        prev_btn.bind('click', lambda e, lid=prev_lesson['id']: navigate('lesson/:id', {'id': lid}))
        nav <= prev_btn
    else:
        nav <= html.SPAN("")

    ids = [l['id'] for l in loader.get_all_lessons()]
    if lesson['id'] in ids:
        nav <= html.SPAN(
            f"Lección {ids.index(lesson['id']) + 1} de {len(ids)}",
            Class="text-sm text-gray-500"
        )

    if next_lesson:
        next_btn = html.BUTTON(
            f"{next_lesson['title']} →",
            Class="px-4 py-2 text-gray-600 hover:text-gray-800"
        )
        next_btn.bind('click', lambda e, lid=next_lesson['id']: navigate('lesson/:id', {'id': lid}))
        nav <= next_btn
    else:
        nav <= html.SPAN("")

    return nav


def _render_complete_button(lesson, state):
    wrapper = html.DIV(Class="text-center py-6")

    btn = html.BUTTON(
        "✓ Marcar como Completada",
        Class="px-8 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
    )

    def on_complete(e):
        progress = state.data.setdefault('progress', {})
        completed = progress.setdefault('lessons_completed', [])

        if lesson['id'] not in completed:
            completed.append(lesson['id'])
            state.save()

            xp = lesson.get('xp_reward', 50)
            award_xp(state, 'lesson_complete', reason="Lección completada")
            check_achievements(state, 'lesson_complete', {'lesson_id': lesson['id']})

            modal = SuccessModal(
                title="¡Lección Completada!",
                message=f"Terminaste «{lesson['title']}».",
                xp_gained=xp
            )
            modal.show()

            btn.innerHTML = "✓ Completada"
            btn.className = "px-8 py-3 bg-gray-400 text-white font-medium rounded-lg cursor-not-allowed"
            btn.disabled = True

    btn.bind('click', on_complete)
    wrapper <= btn

    return wrapper
