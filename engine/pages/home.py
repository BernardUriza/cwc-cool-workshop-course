# PromptCraft - Home Page
# Página principal

from browser import document, html
from ..state import get_state
from ..router import navigate


def home_page(params):
    """
    Renderiza la página principal.

    Args:
        params: Parámetros de la ruta (vacío para home)

    Returns:
        Elemento DOM de la página
    """
    state = get_state()
    level_info = state.get_level_info()

    container = html.DIV(Class="space-y-8")

    # Hero Section
    hero = _render_hero(state, level_info)
    container <= hero

    # Quick Actions
    actions = _render_quick_actions()
    container <= actions

    # Progress Overview
    progress = _render_progress_overview(state)
    container <= progress

    # Continue Learning
    continue_section = _render_continue_learning(state)
    container <= continue_section

    # Daily Challenge
    daily = _render_daily_challenge()
    container <= daily

    return container


def _render_hero(state, level_info):
    """Renderiza la sección hero."""
    hero = html.DIV(Class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white")

    # Saludo personalizado
    from browser import window
    hour = window.Date.new().getHours()
    if hour < 12:
        greeting = "¡Buenos días"
    elif hour < 18:
        greeting = "¡Buenas tardes"
    else:
        greeting = "¡Buenas noches"

    username = state.data.get('user', {}).get('username', 'Prompter')
    hero <= html.H1(f"{greeting}, {username}! 👋", Class="text-2xl font-bold mb-2")
    hero <= html.P(
        "Continúa tu viaje para dominar el arte del Prompt Engineering.",
        Class="text-indigo-100 mb-6"
    )

    # Stats rápidos
    stats_row = html.DIV(Class="grid grid-cols-3 gap-4")

    # Nivel
    stats_row <= html.DIV(
        html.SPAN(f"Nivel {level_info['level']}", Class="block text-2xl font-bold") +
        html.SPAN(level_info['title'], Class="text-indigo-200 text-sm"),
        Class="text-center"
    )

    # XP
    progress_data = state.data.get('progress', {})
    xp_total = progress_data.get('xp', 0)
    stats_row <= html.DIV(
        html.SPAN(str(xp_total), Class="block text-2xl font-bold") +
        html.SPAN("XP Total", Class="text-indigo-200 text-sm"),
        Class="text-center"
    )

    # Racha
    streak_data = state.data.get('streak', {})
    streak = streak_data.get('current', 0)
    stats_row <= html.DIV(
        html.SPAN("🔥 " + str(streak), Class="block text-2xl font-bold") +
        html.SPAN("Días de racha", Class="text-indigo-200 text-sm"),
        Class="text-center"
    )

    hero <= stats_row

    # Barra de XP
    xp_section = html.DIV(Class="mt-6")
    xp_section <= html.DIV(
        html.DIV(
            Class="h-full bg-white/30 rounded-full transition-all",
            style=f"width: {level_info['progress']}%"
        ),
        Class="w-full h-3 bg-white/20 rounded-full overflow-hidden"
    )
    xp_section <= html.P(
        f"{level_info['xp_in_level']} / {level_info['xp_for_next']} XP para nivel {level_info['level'] + 1}",
        Class="text-sm text-indigo-200 mt-2 text-center"
    )
    hero <= xp_section

    return hero


def _render_quick_actions():
    """Renderiza acciones rápidas."""
    section = html.DIV(Class="space-y-4")

    # Título de sección
    section <= html.H2("Explora el Curso", Class="text-lg font-semibold text-gray-800")

    # Grid principal
    grid = html.DIV(Class="grid grid-cols-2 md:grid-cols-4 gap-4")

    actions = [
        ('📚', 'Lecciones', 'lessons', 'bg-blue-50 hover:bg-blue-100 border-blue-200'),
        ('✍️', 'Práctica', 'practice', 'bg-teal-50 hover:bg-teal-100 border-teal-200'),
        ('🧩', 'Puzzles', 'puzzles', 'bg-purple-50 hover:bg-purple-100 border-purple-200'),
        ('🤖', 'Claude Code', 'claude-exercises', 'bg-cyan-50 hover:bg-cyan-100 border-cyan-200'),
    ]

    for icon, label, route, colors in actions:
        card = html.DIV(
            html.SPAN(icon, Class="text-3xl mb-2 block") +
            html.SPAN(label, Class="font-medium text-gray-700"),
            Class=f"p-6 rounded-xl border text-center cursor-pointer transition-colors {colors}"
        )
        card.bind('click', lambda e, r=route: navigate(r))
        grid <= card

    section <= grid

    # Fila secundaria con más acciones
    grid2 = html.DIV(Class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4")

    secondary_actions = [
        ('🎮', 'Playground', 'playground', 'bg-green-50 hover:bg-green-100 border-green-200'),
        ('📝', 'Test Inicial', 'assessment', 'bg-orange-50 hover:bg-orange-100 border-orange-200'),
        ('🎓', 'Proyecto Final', 'final-project', 'bg-indigo-50 hover:bg-indigo-100 border-indigo-200'),
        ('🏆', 'Badges', 'badges', 'bg-yellow-50 hover:bg-yellow-100 border-yellow-200'),
    ]

    for icon, label, route, colors in secondary_actions:
        card = html.DIV(
            html.SPAN(icon, Class="text-3xl mb-2 block") +
            html.SPAN(label, Class="font-medium text-gray-700"),
            Class=f"p-6 rounded-xl border text-center cursor-pointer transition-colors {colors}"
        )
        card.bind('click', lambda e, r=route: navigate(r))
        grid2 <= card

    section <= grid2

    return section


def _render_progress_overview(state):
    """Renderiza resumen de progreso."""
    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100")
    section <= html.H2("Tu Progreso", Class="text-lg font-semibold text-gray-800 mb-4")

    # Grid de progreso
    progress_grid = html.DIV(Class="grid grid-cols-1 md:grid-cols-3 gap-4")

    # Lecciones
    lessons_completed = len(state.data.get('progress', {}).get('lessons_completed', []))
    total_lessons = 20
    lessons_pct = (lessons_completed / total_lessons) * 100

    progress_grid <= html.DIV(
        html.DIV(
            html.SPAN("📖", Class="text-2xl") +
            html.DIV(
                html.SPAN(f"{lessons_completed}/{total_lessons}", Class="font-bold text-gray-800") +
                html.SPAN(" Lecciones", Class="text-gray-500 text-sm"),
                Class="ml-3"
            ),
            Class="flex items-center mb-2"
        ) +
        html.DIV(
            html.DIV(Class=f"h-full bg-blue-500 rounded-full", style=f"width: {lessons_pct}%"),
            Class="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
        ),
        Class="p-4 bg-blue-50 rounded-lg"
    )

    # Puzzles
    puzzles_solved = len(state.data.get('progress', {}).get('puzzles_solved', {}))
    total_puzzles = 15
    puzzles_pct = (puzzles_solved / total_puzzles) * 100

    progress_grid <= html.DIV(
        html.DIV(
            html.SPAN("🧩", Class="text-2xl") +
            html.DIV(
                html.SPAN(f"{puzzles_solved}/{total_puzzles}", Class="font-bold text-gray-800") +
                html.SPAN(" Puzzles", Class="text-gray-500 text-sm"),
                Class="ml-3"
            ),
            Class="flex items-center mb-2"
        ) +
        html.DIV(
            html.DIV(Class=f"h-full bg-purple-500 rounded-full", style=f"width: {puzzles_pct}%"),
            Class="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
        ),
        Class="p-4 bg-purple-50 rounded-lg"
    )

    # Badges
    badges_unlocked = len(state.data.get('badges', []))
    total_badges = 30
    badges_pct = (badges_unlocked / total_badges) * 100

    progress_grid <= html.DIV(
        html.DIV(
            html.SPAN("🏆", Class="text-2xl") +
            html.DIV(
                html.SPAN(f"{badges_unlocked}/{total_badges}", Class="font-bold text-gray-800") +
                html.SPAN(" Badges", Class="text-gray-500 text-sm"),
                Class="ml-3"
            ),
            Class="flex items-center mb-2"
        ) +
        html.DIV(
            html.DIV(Class=f"h-full bg-yellow-500 rounded-full", style=f"width: {badges_pct}%"),
            Class="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
        ),
        Class="p-4 bg-yellow-50 rounded-lg"
    )

    section <= progress_grid

    return section


def _render_continue_learning(state):
    """Renderiza sección de continuar aprendiendo."""
    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100")
    section <= html.H2("Continuar Aprendiendo", Class="text-lg font-semibold text-gray-800 mb-4")

    # Sugerencias basadas en progreso
    suggestions = html.DIV(Class="grid grid-cols-1 md:grid-cols-2 gap-4")

    # Próxima lección
    lesson_card = html.DIV(
        html.DIV(
            html.SPAN("📚", Class="text-xl") +
            html.SPAN("Próxima Lección", Class="ml-2 font-medium text-gray-700"),
            Class="flex items-center mb-2"
        ) +
        html.P("Técnicas de Few-Shot Prompting", Class="text-gray-600 text-sm mb-3") +
        html.BUTTON(
            "Continuar →",
            Class="text-sm text-indigo-600 font-medium hover:text-indigo-800"
        ),
        Class="p-4 border border-gray-200 rounded-lg hover:border-indigo-200 cursor-pointer transition-colors"
    )
    lesson_card.bind('click', lambda e: navigate('lessons'))
    suggestions <= lesson_card

    # Próximo puzzle
    puzzle_card = html.DIV(
        html.DIV(
            html.SPAN("🧩", Class="text-xl") +
            html.SPAN("Puzzle Recomendado", Class="ml-2 font-medium text-gray-700"),
            Class="flex items-center mb-2"
        ) +
        html.P("El Misterio del Prompt Perfecto", Class="text-gray-600 text-sm mb-3") +
        html.BUTTON(
            "Resolver →",
            Class="text-sm text-purple-600 font-medium hover:text-purple-800"
        ),
        Class="p-4 border border-gray-200 rounded-lg hover:border-purple-200 cursor-pointer transition-colors"
    )
    puzzle_card.bind('click', lambda e: navigate('puzzles'))
    suggestions <= puzzle_card

    section <= suggestions

    return section


def _render_daily_challenge():
    """Renderiza el desafío diario."""
    section = html.DIV(Class="bg-gradient-to-r from-amber-400 to-orange-500 rounded-xl p-6 text-white")

    header = html.DIV(Class="flex items-center justify-between mb-4")
    header <= html.DIV(
        html.SPAN("⚡", Class="text-2xl mr-2") +
        html.SPAN("Desafío Diario", Class="text-xl font-bold"),
        Class="flex items-center"
    )
    header <= html.SPAN("+100 XP", Class="bg-white/20 px-3 py-1 rounded-full text-sm font-medium")

    section <= header

    section <= html.P(
        "Completa una lección y resuelve un puzzle hoy para ganar bonus de XP.",
        Class="text-amber-100 mb-4"
    )

    # Progreso del desafío
    progress = html.DIV(Class="flex items-center gap-4")
    progress <= html.DIV(
        html.SPAN("✓", Class="text-green-400 mr-1") + "1 Lección",
        Class="text-sm"
    )
    progress <= html.DIV(
        html.SPAN("○", Class="mr-1") + "1 Puzzle",
        Class="text-sm text-amber-200"
    )
    section <= progress

    return section
