# CWC - Puzzles Page

from browser import html
from ..state import get_state
from ..router import navigate
from ..components.card import PuzzleCard
from ..components.tabs import Tabs
from ..config import http_get_json

_index = None


def _get_index():
    global _index
    if _index is None:
        _index = http_get_json('content/puzzles/index.json') or {'categories': [], 'puzzles': []}
    return _index


def solved_puzzles(state):
    """Mapa unificado de puzzles resueltos (progress.puzzles_solved + legado)."""
    merged = dict(state.data.get('puzzles_completed', {}))
    merged.update(state.data.get('progress', {}).get('puzzles_solved', {}))
    return merged


def puzzles_page(params):
    state = get_state()

    container = html.DIV(Class="max-w-5xl mx-auto")

    header = html.DIV(Class="mb-8")
    header <= html.H1("🧩 Puzzles de Lógica", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(
        "Pon a prueba tus conocimientos con puzzles de eliminación lógica.",
        Class="text-gray-600"
    )
    container <= header

    container <= _render_stats(state)
    container <= _render_how_to_play()
    container <= _render_puzzles_tabs(state)

    return container


def _render_stats(state):
    completed = solved_puzzles(state)
    total_puzzles = len(_get_index()['puzzles'])
    solved = len(completed)
    three_stars = len([p for p in completed.values() if p.get('best_stars', 0) == 3])

    stats = html.DIV(Class="grid grid-cols-3 gap-4 mb-8")

    stats <= html.DIV(
        html.SPAN(str(solved), Class="text-3xl font-bold text-purple-600") +
        html.SPAN(f"/{total_puzzles}", Class="text-xl text-gray-400") +
        html.P("Puzzles resueltos", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    stats <= html.DIV(
        html.SPAN("⭐⭐⭐", Class="text-xl") +
        html.SPAN(f" {three_stars}", Class="text-2xl font-bold text-yellow-500") +
        html.P("Perfectos", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    best_time = None
    for p in completed.values():
        t = p.get('best_time')
        if t and (best_time is None or t < best_time):
            best_time = t

    if best_time:
        mins = best_time // 60
        secs = best_time % 60
        time_str = f"{mins}:{secs:02d}"
    else:
        time_str = "--:--"

    stats <= html.DIV(
        html.SPAN(time_str, Class="text-2xl font-bold text-green-600") +
        html.P("Mejor tiempo", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    return stats


def _render_how_to_play():
    section = html.DIV(Class="bg-indigo-50 rounded-xl p-6 border border-indigo-100 mb-8")

    section <= html.H3("¿Cómo se juega?", Class="font-semibold text-indigo-800 mb-4")

    steps = [
        ("1", "Lee las pistas", "Cada puzzle tiene pistas que te ayudarán a deducir las relaciones."),
        ("2", "Marca la tabla", "Usa ✓ para confirmar y ✗ para eliminar. Haz clic para cambiar."),
        ("3", "Deduce y gana", "Completa la tabla correctamente para resolver el puzzle."),
    ]

    instructions = html.DIV(Class="grid grid-cols-1 md:grid-cols-3 gap-4")
    for num, title, desc in steps:
        instructions <= html.DIV(
            html.SPAN(num, Class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold mb-2") +
            html.P(title, Class="font-medium text-gray-700") +
            html.P(desc, Class="text-sm text-gray-600"),
            Class="text-center"
        )
    section <= instructions

    return section


def _render_puzzles_tabs(state):
    index = _get_index()
    used_categories = {p.get('category') for p in index['puzzles']}

    categories = [{'id': 'all', 'label': 'Todos', 'icon': '📋'}]
    for cat in index['categories']:
        if cat['id'] in used_categories:
            categories.append({'id': cat['id'], 'label': cat['name'], 'icon': cat.get('icon', '📂')})

    tabs_data = [{
        'id': cat['id'],
        'label': cat['label'],
        'icon': cat['icon'],
        'content': lambda c=cat['id']: _render_puzzle_list(state, c)
    } for cat in categories]

    return Tabs(tabs=tabs_data, active_tab='all', variant='pills').render()


def _render_puzzle_list(state, category):
    puzzles = _get_puzzles(category)
    completed = solved_puzzles(state)

    grid = html.DIV(Class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4")

    for puzzle in puzzles:
        puzzle_id = puzzle['id']

        if puzzle_id in completed:
            puzzle['solved'] = True
            best_time = completed[puzzle_id].get('best_time')
            if best_time:
                mins = best_time // 60
                secs = best_time % 60
                puzzle['best_time'] = f"{mins}:{secs:02d}"

        grid <= PuzzleCard(
            puzzle=puzzle,
            on_click=lambda pid: navigate('puzzle/:id', {'id': pid})
        ).render()

    if not puzzles:
        grid <= html.DIV(
            html.SPAN("🧩", Class="text-4xl text-gray-300") +
            html.P("No hay puzzles en esta categoría aún.", Class="text-gray-400 mt-2"),
            Class="col-span-full text-center py-12"
        )

    return grid


def _get_puzzles(category='all'):
    puzzles = [dict(p) for p in _get_index()['puzzles']]
    if category == 'all':
        return puzzles
    return [p for p in puzzles if p.get('category') == category]
