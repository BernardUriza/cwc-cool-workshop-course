# PromptCraft - Profile Page
# Página de perfil del usuario

from browser import document, html
from ..state import get_state
from ..router import navigate
from ..components.progress import XPBar, LevelBadge
from ..components.badge_display import BadgeGrid
from ..gamification.levels import LevelSystem, LEVEL_TITLES, LEVEL_ICONS
from ..gamification.badges import BadgeManager
from ..gamification.streaks import StreakManager
from ..gamification.achievements import AchievementTracker


def profile_page(params):
    """
    Renderiza la página de perfil.

    Args:
        params: Parámetros de la ruta

    Returns:
        Elemento DOM de la página
    """
    state = get_state()

    container = html.DIV(Class="max-w-4xl mx-auto")

    # Header del perfil
    header = _render_profile_header(state)
    container <= header

    # Estadísticas
    stats = _render_stats(state)
    container <= stats

    # Nivel y progreso
    level_section = _render_level_section(state)
    container <= level_section

    # Calendario de actividad
    calendar = _render_activity_calendar(state)
    container <= calendar

    # Badges recientes
    badges = _render_recent_badges(state)
    container <= badges

    # Historial de XP
    xp_history = _render_xp_history(state)
    container <= xp_history

    return container


def _render_profile_header(state):
    """Renderiza el header del perfil."""
    level_info = state.get_level_info()
    streak = state.data.get('streak', {}).get('current', 0)

    header = html.DIV(Class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white mb-8")

    # Avatar y nombre
    profile_row = html.DIV(Class="flex items-center gap-6")

    # Avatar/Nivel badge
    avatar = html.DIV(
        html.SPAN(LEVEL_ICONS.get(level_info['level'], '🎯'), Class="text-5xl"),
        Class="w-24 h-24 rounded-full bg-white/20 flex items-center justify-center"
    )
    profile_row <= avatar

    # Info
    info = html.DIV()
    username = state.data.get('username', 'Prompter')
    info <= html.H1(username, Class="text-3xl font-bold")
    info <= html.P(
        f"Nivel {level_info['level']} - {level_info['title']}",
        Class="text-indigo-200 text-lg"
    )

    # Stats rápidos
    quick_stats = html.DIV(Class="flex gap-6 mt-4")
    quick_stats <= html.DIV(
        html.SPAN(f"{state.data.get('xp', 0)}", Class="font-bold text-xl") +
        html.SPAN(" XP", Class="text-indigo-200")
    )
    quick_stats <= html.DIV(
        html.SPAN(f"🔥 {streak}", Class="font-bold text-xl") +
        html.SPAN(" días", Class="text-indigo-200")
    )
    quick_stats <= html.DIV(
        html.SPAN(f"🏆 {len(state.data.get('badges', []))}", Class="font-bold text-xl") +
        html.SPAN(" badges", Class="text-indigo-200")
    )
    info <= quick_stats

    profile_row <= info

    header <= profile_row

    # Barra de progreso de nivel
    progress_section = html.DIV(Class="mt-6")
    progress_section <= html.DIV(
        html.DIV(
            Class="h-full bg-white/30 rounded-full transition-all",
            style=f"width: {level_info['progress']}%"
        ),
        Class="w-full h-3 bg-white/20 rounded-full overflow-hidden"
    )
    progress_section <= html.P(
        f"{level_info['xp_in_level']} / {level_info['xp_for_next']} XP para nivel {level_info['level'] + 1}",
        Class="text-sm text-indigo-200 mt-2"
    )
    header <= progress_section

    return header


def _render_stats(state):
    """Renderiza estadísticas del usuario."""
    tracker = AchievementTracker(state)
    all_stats = tracker.get_all_stats()

    section = html.DIV(Class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8")

    stats_data = [
        ('📚', str(all_stats['lessons']['completed']), 'Lecciones'),
        ('🧩', str(all_stats['puzzles']['solved']), 'Puzzles'),
        ('⭐', str(all_stats['puzzles']['three_stars']), '3 Estrellas'),
        ('🏆', str(all_stats['badges']['unlocked']), 'Badges'),
    ]

    for icon, value, label in stats_data:
        card = html.DIV(
            html.SPAN(icon, Class="text-2xl") +
            html.SPAN(value, Class="text-3xl font-bold text-gray-800 ml-2") +
            html.P(label, Class="text-sm text-gray-500 mt-1"),
            Class="bg-white rounded-xl p-4 border border-gray-100 text-center"
        )
        section <= card

    return section


def _render_level_section(state):
    """Renderiza sección de niveles."""
    level_info = state.get_level_info()
    level_system = LevelSystem()
    all_levels = level_system.get_all_levels()

    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100 mb-8")
    section <= html.H2("🎖️ Tu Progreso de Nivel", Class="text-xl font-semibold text-gray-800 mb-4")

    # Grid de niveles
    levels_grid = html.DIV(Class="grid grid-cols-5 md:grid-cols-10 gap-2")

    for lvl in all_levels:
        is_current = lvl['level'] == level_info['level']
        is_achieved = lvl['level'] <= level_info['level']

        if is_achieved:
            level_class = "bg-indigo-600 text-white"
        else:
            level_class = "bg-gray-100 text-gray-400"

        if is_current:
            level_class += " ring-2 ring-indigo-400 ring-offset-2"

        level_item = html.DIV(
            html.SPAN(lvl['icon'], Class="text-lg") +
            html.SPAN(str(lvl['level']), Class="text-xs font-bold block"),
            Class=f"w-12 h-12 rounded-full flex flex-col items-center justify-center {level_class}",
            title=f"Nivel {lvl['level']}: {lvl['title']}\n{lvl['xp_required']} XP requerido"
        )
        levels_grid <= level_item

    section <= levels_grid

    return section


def _render_activity_calendar(state):
    """Renderiza calendario de actividad."""
    streak_mgr = StreakManager(state)
    calendar = streak_mgr.get_calendar(30)
    streak_info = streak_mgr.get_info()

    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100 mb-8")

    # Header
    header = html.DIV(Class="flex items-center justify-between mb-4")
    header <= html.H2("📅 Actividad (últimos 30 días)", Class="text-xl font-semibold text-gray-800")
    header <= html.DIV(
        html.SPAN("🔥 ", Class="text-lg") +
        html.SPAN(f"{streak_info['current']} días", Class="font-bold text-orange-500") +
        html.SPAN(" de racha", Class="text-gray-500 text-sm"),
        Class="flex items-center"
    )
    section <= header

    # Calendario
    cal_grid = html.DIV(Class="grid grid-cols-10 md:grid-cols-15 gap-1")

    for day in calendar:
        if day['active']:
            day_class = "bg-green-500"
        else:
            day_class = "bg-gray-200"

        if day['is_today']:
            day_class += " ring-2 ring-indigo-400"

        day_elem = html.DIV(
            Class=f"w-6 h-6 rounded {day_class}",
            title=day['date']
        )
        cal_grid <= day_elem

    section <= cal_grid

    # Leyenda
    legend = html.DIV(Class="flex items-center gap-4 mt-4 text-sm text-gray-500")
    legend <= html.DIV(
        html.DIV(Class="w-4 h-4 rounded bg-gray-200 inline-block mr-1") +
        html.SPAN("Sin actividad")
    )
    legend <= html.DIV(
        html.DIV(Class="w-4 h-4 rounded bg-green-500 inline-block mr-1") +
        html.SPAN("Día activo")
    )
    section <= legend

    # Freezes disponibles
    freezes = streak_info.get('freezes', 0)
    if freezes > 0:
        section <= html.P(
            f"❄️ Tienes {freezes} freeze(s) de racha disponibles",
            Class="text-sm text-blue-600 mt-3"
        )

    return section


def _render_recent_badges(state):
    """Renderiza badges recientes."""
    badge_mgr = BadgeManager(state)
    unlocked = badge_mgr.get_unlocked()

    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100 mb-8")

    header = html.DIV(Class="flex items-center justify-between mb-4")
    header <= html.H2("🏆 Badges Desbloqueados", Class="text-xl font-semibold text-gray-800")
    header <= html.A(
        "Ver todos →",
        href="#badges",
        Class="text-indigo-600 hover:text-indigo-800 text-sm"
    )
    section <= header

    if unlocked:
        # Mostrar últimos 5
        recent = sorted(unlocked, key=lambda b: b.get('unlocked_at', ''), reverse=True)[:5]

        grid = html.DIV(Class="flex flex-wrap gap-4")
        for badge in recent:
            badge_elem = html.DIV(
                html.SPAN(badge['icon'], Class="text-3xl") +
                html.P(badge['name'], Class="text-xs text-gray-600 mt-1 text-center"),
                Class="flex flex-col items-center p-3 bg-gray-50 rounded-lg"
            )
            grid <= badge_elem
        section <= grid
    else:
        section <= html.P(
            "Aún no has desbloqueado ningún badge. ¡Completa lecciones y puzzles para ganarlos!",
            Class="text-gray-400 italic text-center py-4"
        )

    return section


def _render_xp_history(state):
    """Renderiza historial de XP."""
    history = state.data.get('xp_history', [])[-10:]
    history = list(reversed(history))

    section = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100")
    section <= html.H2("📊 Historial de XP", Class="text-xl font-semibold text-gray-800 mb-4")

    if history:
        list_elem = html.DIV(Class="space-y-2")
        for event in history:
            activity = event.get('activity', 'actividad').replace('_', ' ').title()
            amount = event.get('amount', 0)

            item = html.DIV(
                html.SPAN(f"+{amount} XP", Class="font-bold text-indigo-600 w-20") +
                html.SPAN(activity, Class="text-gray-700"),
                Class="flex items-center p-2 hover:bg-gray-50 rounded"
            )
            list_elem <= item
        section <= list_elem
    else:
        section <= html.P(
            "Tu historial de XP aparecerá aquí.",
            Class="text-gray-400 italic text-center py-4"
        )

    return section
