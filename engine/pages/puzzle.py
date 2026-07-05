# PromptCraft - Puzzle Detail Page
# Página de puzzle individual

from browser import document, html
from ..state import get_state
from ..router import navigate
from ..puzzles.logic_puzzle import LogicPuzzle
from ..puzzles.loader import get_embedded_puzzle, load_puzzle
from ..gamification.achievements import check_achievements
from ..gamification.xp import award_xp


def puzzle_page(params):
    """
    Renderiza la página de un puzzle.

    Args:
        params: Dict con 'id' del puzzle

    Returns:
        Elemento DOM de la página
    """
    puzzle_id = params.get('id', '')
    state = get_state()

    container = html.DIV(Class="max-w-6xl mx-auto")

    # Breadcrumb
    breadcrumb = html.DIV(Class="mb-6")
    breadcrumb <= html.A(
        "← Volver a Puzzles",
        href="#puzzles",
        Class="text-indigo-600 hover:text-indigo-800"
    )
    container <= breadcrumb

    # Obtener datos del puzzle
    puzzle_data = get_embedded_puzzle(puzzle_id)

    if not puzzle_data:
        container <= _render_not_found(puzzle_id)
        return container

    # Verificar si ya está completado
    completed = state.data.get('puzzles_completed', {}).get(puzzle_id, {})
    if completed.get('solved'):
        container <= _render_completed_banner(completed)

    # Renderizar puzzle
    puzzle_component = LogicPuzzle(
        puzzle_data=puzzle_data,
        on_complete=lambda result: _on_puzzle_complete(puzzle_id, result, state),
        on_exit=lambda: navigate('puzzles')
    )

    container <= puzzle_component.render()
    puzzle_component.on_mount()

    return container


def _render_not_found(puzzle_id):
    """Renderiza mensaje de puzzle no encontrado."""
    return html.DIV(
        html.SPAN("🧩", Class="text-6xl text-gray-300") +
        html.H1(f"Puzzle '{puzzle_id}' no encontrado", Class="text-xl font-bold text-gray-700 mt-4") +
        html.P("Este puzzle no existe o aún no está disponible.", Class="text-gray-500 mt-2") +
        html.A(
            "← Volver a Puzzles",
            href="#puzzles",
            Class="mt-4 inline-block text-indigo-600 hover:text-indigo-800"
        ),
        Class="text-center py-16"
    )


def _render_completed_banner(completed):
    """Renderiza banner de puzzle ya completado."""
    best_time = completed.get('best_time', 0)
    mins = best_time // 60
    secs = best_time % 60
    stars = completed.get('best_stars', 0)

    banner = html.DIV(Class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6")

    content = html.DIV(Class="flex items-center justify-between")

    # Info
    info = html.DIV(Class="flex items-center gap-3")
    info <= html.SPAN("✅", Class="text-2xl")
    info <= html.DIV(
        html.P("¡Ya resolviste este puzzle!", Class="font-medium text-green-700") +
        html.P(f"Mejor tiempo: {mins}:{secs:02d}", Class="text-sm text-green-600")
    )
    content <= info

    # Estrellas
    stars_div = html.DIV(Class="flex gap-1")
    for i in range(3):
        star_class = "text-yellow-400 text-xl" if i < stars else "text-gray-300 text-xl"
        stars_div <= html.SPAN("★", Class=star_class)
    content <= stars_div

    banner <= content

    # Opción de reintentar
    banner <= html.P(
        "Puedes volver a jugarlo para mejorar tu tiempo y estrellas.",
        Class="text-sm text-green-600 mt-2"
    )

    return banner


def _on_puzzle_complete(puzzle_id, result, state):
    """Callback cuando se completa un puzzle."""
    # Guardar resultado
    if 'puzzles_completed' not in state.data:
        state.data['puzzles_completed'] = {}

    existing = state.data['puzzles_completed'].get(puzzle_id, {})

    # Actualizar mejor resultado
    if not existing.get('best_time') or result['time'] < existing.get('best_time', 999999):
        existing['best_time'] = result['time']

    if result['stars'] > existing.get('best_stars', 0):
        existing['best_stars'] = result['stars']

    existing['solved'] = True
    existing['attempts'] = existing.get('attempts', 0) + 1

    state.data['puzzles_completed'][puzzle_id] = existing
    state.save()

    # Otorgar XP
    modifiers = {}
    if result['hints_used'] == 0:
        modifiers['no_hints_bonus'] = True
    if result['stars'] == 3:
        modifiers['perfect_bonus'] = True
    if result['time'] < 120:
        modifiers['speed_bonus'] = True

    award_xp(state, 'puzzle_solve', result.get('xp', 75), modifiers, "Puzzle completado")

    # Verificar achievements
    check_achievements(state, 'puzzle_complete', {
        'puzzle_id': puzzle_id,
        'time': result['time'],
        'stars': result['stars'],
        'hints_used': result['hints_used']
    })

    # Actualizar streak
    from ..gamification.streaks import StreakManager
    streak_mgr = StreakManager(state)
    streak_mgr.update()
    streak_mgr.record_activity()
