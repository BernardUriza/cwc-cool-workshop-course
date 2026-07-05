# PromptCraft - Puzzles Page
# Página de lista de puzzles

from browser import document, html
from ..state import get_state
from ..router import navigate
from ..components.card import PuzzleCard
from ..components.tabs import Tabs


def puzzles_page(params):
    """
    Renderiza la página de puzzles.

    Args:
        params: Parámetros de la ruta

    Returns:
        Elemento DOM de la página
    """
    state = get_state()

    container = html.DIV(Class="max-w-5xl mx-auto")

    # Header
    header = html.DIV(Class="mb-8")
    header <= html.H1("🧩 Puzzles de Lógica", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(
        "Pon a prueba tus conocimientos con puzzles de eliminación lógica sobre Prompt Engineering.",
        Class="text-gray-600"
    )
    container <= header

    # Estadísticas
    stats = _render_stats(state)
    container <= stats

    # Descripción de cómo jugar
    how_to = _render_how_to_play()
    container <= how_to

    # Tabs por categoría
    tabs_content = _render_puzzles_tabs(state)
    container <= tabs_content

    return container


def _render_stats(state):
    """Renderiza estadísticas de puzzles."""
    puzzles_completed = state.data.get('puzzles_completed', {})
    total_puzzles = 15
    solved = len(puzzles_completed)
    three_stars = len([p for p in puzzles_completed.values() if p.get('best_stars', 0) == 3])

    stats = html.DIV(Class="grid grid-cols-3 gap-4 mb-8")

    # Resueltos
    stats <= html.DIV(
        html.SPAN(str(solved), Class="text-3xl font-bold text-purple-600") +
        html.SPAN(f"/{total_puzzles}", Class="text-xl text-gray-400") +
        html.P("Puzzles resueltos", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    # 3 estrellas
    stats <= html.DIV(
        html.SPAN("⭐⭐⭐", Class="text-xl") +
        html.SPAN(f" {three_stars}", Class="text-2xl font-bold text-yellow-500") +
        html.P("Perfectos", Class="text-sm text-gray-500 mt-1"),
        Class="bg-white rounded-lg p-4 border border-gray-100 text-center"
    )

    # Mejor tiempo
    best_time = None
    for p in puzzles_completed.values():
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
    """Renderiza instrucciones de cómo jugar."""
    section = html.DIV(Class="bg-indigo-50 rounded-xl p-6 border border-indigo-100 mb-8")

    section <= html.H3("¿Cómo se juega?", Class="font-semibold text-indigo-800 mb-4")

    instructions = html.DIV(Class="grid grid-cols-1 md:grid-cols-3 gap-4")

    # Paso 1
    instructions <= html.DIV(
        html.SPAN("1", Class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold mb-2") +
        html.P("Lee las pistas", Class="font-medium text-gray-700") +
        html.P("Cada puzzle tiene pistas que te ayudarán a deducir las relaciones.", Class="text-sm text-gray-600"),
        Class="text-center"
    )

    # Paso 2
    instructions <= html.DIV(
        html.SPAN("2", Class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold mb-2") +
        html.P("Marca la tabla", Class="font-medium text-gray-700") +
        html.P("Usa ✓ para confirmar y ✗ para eliminar. Haz clic para cambiar.", Class="text-sm text-gray-600"),
        Class="text-center"
    )

    # Paso 3
    instructions <= html.DIV(
        html.SPAN("3", Class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold mb-2") +
        html.P("Deduce y gana", Class="font-medium text-gray-700") +
        html.P("Completa la tabla correctamente para resolver el puzzle.", Class="text-sm text-gray-600"),
        Class="text-center"
    )

    section <= instructions

    return section


def _render_puzzles_tabs(state):
    """Renderiza tabs de puzzles por categoría."""
    categories = [
        {'id': 'all', 'label': 'Todos', 'icon': '📋'},
        {'id': 'fundamentos', 'label': 'Fundamentos', 'icon': '📚'},
        {'id': 'tecnicas', 'label': 'Técnicas', 'icon': '🎯'},
        {'id': 'avanzado', 'label': 'Avanzado', 'icon': '🚀'},
    ]

    tabs_data = []
    for cat in categories:
        tabs_data.append({
            'id': cat['id'],
            'label': cat['label'],
            'icon': cat['icon'],
            'content': lambda c=cat['id']: _render_puzzle_list(state, c)
        })

    tabs = Tabs(
        tabs=tabs_data,
        active_tab='all',
        variant='pills'
    )

    return tabs.render()


def _render_puzzle_list(state, category):
    """Renderiza lista de puzzles."""
    puzzles = _get_puzzles(category)
    completed = state.data.get('puzzles_completed', {})

    grid = html.DIV(Class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4")

    for puzzle in puzzles:
        puzzle_id = puzzle['id']

        # Añadir info de completado
        if puzzle_id in completed:
            puzzle['solved'] = True
            best_time = completed[puzzle_id].get('best_time')
            if best_time:
                mins = best_time // 60
                secs = best_time % 60
                puzzle['best_time'] = f"{mins}:{secs:02d}"

        card = PuzzleCard(
            puzzle=puzzle,
            on_click=lambda pid: navigate('puzzle/:id', {'id': pid})
        ).render()

        grid <= card

    if not puzzles:
        grid <= html.DIV(
            html.SPAN("🧩", Class="text-4xl text-gray-300") +
            html.P("No hay puzzles en esta categoría aún.", Class="text-gray-400 mt-2"),
            Class="col-span-full text-center py-12"
        )

    return grid


def _get_puzzles(category='all'):
    """Obtiene lista de puzzles."""
    all_puzzles = [
        # Fundamentos
        {
            'id': 'intro-01',
            'title': 'El Primer Prompt',
            'description': 'Descubre quién usó cada técnica básica.',
            'category': 'fundamentos',
            'difficulty': 1,
            'xp_reward': 50,
        },
        {
            'id': 'components-01',
            'title': 'Anatomía del Prompt',
            'description': 'Relaciona componentes con sus funciones.',
            'category': 'fundamentos',
            'difficulty': 1,
            'xp_reward': 50,
        },
        {
            'id': 'clarity-01',
            'title': 'Claridad ante Todo',
            'description': 'Encuentra las combinaciones correctas de claridad.',
            'category': 'fundamentos',
            'difficulty': 2,
            'xp_reward': 75,
        },

        # Técnicas
        {
            'id': 'roles-01',
            'title': 'Maestro de Roles',
            'description': 'Descubre qué rol usó cada experto.',
            'category': 'tecnicas',
            'difficulty': 2,
            'xp_reward': 75,
        },
        {
            'id': 'chain-01',
            'title': 'Cadena de Pensamiento',
            'description': 'Ordena los pasos del razonamiento.',
            'category': 'tecnicas',
            'difficulty': 3,
            'xp_reward': 100,
        },
        {
            'id': 'fewshot-01',
            'title': 'El Poder de los Ejemplos',
            'description': 'Relaciona ejemplos con resultados.',
            'category': 'tecnicas',
            'difficulty': 3,
            'xp_reward': 100,
        },
        {
            'id': 'techniques-mix-01',
            'title': 'Combinación Perfecta',
            'description': 'Descubre las combinaciones de técnicas.',
            'category': 'tecnicas',
            'difficulty': 4,
            'xp_reward': 125,
        },

        # Avanzado
        {
            'id': 'tree-01',
            'title': 'Árbol de Decisiones',
            'description': 'Resuelve el misterio del Tree of Thoughts.',
            'category': 'avanzado',
            'difficulty': 4,
            'xp_reward': 125,
        },
        {
            'id': 'react-01',
            'title': 'Razona y Actúa',
            'description': 'El patrón ReAct en acción.',
            'category': 'avanzado',
            'difficulty': 5,
            'xp_reward': 150,
        },
        {
            'id': 'master-01',
            'title': 'El Gran Desafío',
            'description': 'Demuestra tu dominio total.',
            'category': 'avanzado',
            'difficulty': 5,
            'xp_reward': 200,
        },
    ]

    if category == 'all':
        return all_puzzles

    return [p for p in all_puzzles if p.get('category') == category]
