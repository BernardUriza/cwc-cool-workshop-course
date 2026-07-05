# PromptCraft - Badges Page
# Página de todos los badges

from browser import document, html
from ..state import get_state
from ..components.badge_display import BadgeDisplay, BadgeGrid, BadgeProgress
from ..components.tabs import Tabs
from ..gamification.badges import BadgeManager, BADGES


def badges_page(params):
    """
    Renderiza la página de badges.

    Args:
        params: Parámetros de la ruta

    Returns:
        Elemento DOM de la página
    """
    state = get_state()
    badge_mgr = BadgeManager(state)

    container = html.DIV(Class="max-w-5xl mx-auto")

    # Header
    header = _render_header(badge_mgr)
    container <= header

    # Estadísticas
    stats = _render_stats(badge_mgr)
    container <= stats

    # Tabs por categoría
    tabs = _render_badges_tabs(badge_mgr, state)
    container <= tabs

    return container


def _render_header(badge_mgr):
    """Renderiza el header de la página."""
    stats = badge_mgr.get_stats()

    header = html.DIV(Class="mb-8")
    header <= html.H1("🏆 Colección de Badges", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(
        f"Has desbloqueado {stats['unlocked']} de {stats['total']} badges ({stats['percentage']:.0f}%)",
        Class="text-gray-600"
    )
    return header


def _render_stats(badge_mgr):
    """Renderiza estadísticas de badges por rareza."""
    stats = badge_mgr.get_stats()
    by_rarity = stats['by_rarity']

    section = html.DIV(Class="grid grid-cols-4 gap-4 mb-8")

    rarities = [
        ('common', 'Común', 'bg-gray-100 text-gray-700 border-gray-300'),
        ('rare', 'Raro', 'bg-blue-100 text-blue-700 border-blue-300'),
        ('epic', 'Épico', 'bg-purple-100 text-purple-700 border-purple-300'),
        ('legendary', 'Legendario', 'bg-yellow-100 text-yellow-700 border-yellow-300'),
    ]

    for rarity, label, colors in rarities:
        data = by_rarity.get(rarity, {'total': 0, 'have': 0})
        progress = (data['have'] / data['total'] * 100) if data['total'] > 0 else 0

        card = html.DIV(Class=f"rounded-xl p-4 border-2 {colors}")
        card <= html.P(label, Class="font-medium text-sm mb-1")
        card <= html.P(
            f"{data['have']}/{data['total']}",
            Class="text-2xl font-bold"
        )
        # Progress bar
        card <= html.DIV(
            html.DIV(Class=f"h-full bg-current opacity-50 rounded-full", style=f"width: {progress}%"),
            Class="w-full h-1.5 bg-black/10 rounded-full overflow-hidden mt-2"
        )
        section <= card

    return section


def _render_badges_tabs(badge_mgr, state):
    """Renderiza tabs de badges."""
    categories = [
        {'id': 'all', 'label': 'Todos', 'icon': '📋'},
        {'id': 'progress', 'label': 'Progreso', 'icon': '📈'},
        {'id': 'puzzles', 'label': 'Puzzles', 'icon': '🧩'},
        {'id': 'streak', 'label': 'Racha', 'icon': '🔥'},
        {'id': 'xp', 'label': 'XP/Nivel', 'icon': '⭐'},
        {'id': 'techniques', 'label': 'Técnicas', 'icon': '🎯'},
        {'id': 'special', 'label': 'Especiales', 'icon': '✨'},
    ]

    tabs_data = []
    for cat in categories:
        tabs_data.append({
            'id': cat['id'],
            'label': cat['label'],
            'icon': cat['icon'],
            'content': lambda c=cat['id']: _render_badges_grid(badge_mgr, state, c)
        })

    tabs = Tabs(
        tabs=tabs_data,
        active_tab='all',
        variant='pills'
    )

    return tabs.render()


def _render_badges_grid(badge_mgr, state, category):
    """Renderiza grid de badges de una categoría."""
    if category == 'all':
        badges = badge_mgr.get_all()
    else:
        badges = badge_mgr.get_by_category(category)

    # Ordenar: desbloqueados primero, luego por rareza
    rarity_order = {'legendary': 0, 'epic': 1, 'rare': 2, 'common': 3}
    badges.sort(key=lambda b: (
        not b.get('unlocked', False),
        rarity_order.get(b.get('rarity', 'common'), 3)
    ))

    container = html.DIV()

    # Sección de desbloqueados
    unlocked = [b for b in badges if b.get('unlocked')]
    if unlocked:
        container <= html.H3(
            f"✅ Desbloqueados ({len(unlocked)})",
            Class="font-medium text-gray-700 mb-4"
        )
        container <= _render_badge_section(unlocked)

    # Sección de bloqueados
    locked = [b for b in badges if not b.get('unlocked')]
    if locked:
        container <= html.H3(
            f"🔒 Por Desbloquear ({len(locked)})",
            Class="font-medium text-gray-700 mb-4 mt-8"
        )
        container <= _render_badge_section(locked, show_progress=True, state=state)

    if not badges:
        container <= html.DIV(
            html.SPAN("🏆", Class="text-4xl text-gray-300") +
            html.P("No hay badges en esta categoría.", Class="text-gray-400 mt-2"),
            Class="text-center py-12"
        )

    return container


def _render_badge_section(badges, show_progress=False, state=None):
    """Renderiza una sección de badges."""
    grid = html.DIV(Class="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-6 gap-4 mb-6")

    for badge in badges:
        badge_elem = _render_badge_item(badge, show_progress, state)
        grid <= badge_elem

    return grid


def _render_badge_item(badge, show_progress=False, state=None):
    """Renderiza un item de badge."""
    is_unlocked = badge.get('unlocked', False)
    rarity = badge.get('rarity', 'common')

    # Colores según rareza
    rarity_styles = {
        'common': 'border-gray-300 bg-gray-50',
        'rare': 'border-blue-300 bg-blue-50',
        'epic': 'border-purple-300 bg-purple-50',
        'legendary': 'border-yellow-300 bg-yellow-50',
    }

    style = rarity_styles.get(rarity, rarity_styles['common'])

    container = html.DIV(
        Class=f"p-4 rounded-xl border-2 {style} {'opacity-60' if not is_unlocked else ''} transition-all hover:scale-105"
    )

    # Icono
    icon_size = "text-4xl" if is_unlocked else "text-3xl"
    icon = badge.get('icon', '🏆') if is_unlocked else '🔒'
    container <= html.DIV(
        html.SPAN(icon, Class=icon_size),
        Class="text-center mb-2"
    )

    # Nombre
    container <= html.P(
        badge.get('name', 'Badge'),
        Class="font-medium text-gray-800 text-sm text-center"
    )

    # Descripción en tooltip
    container <= html.P(
        badge.get('description', ''),
        Class="text-xs text-gray-500 text-center mt-1 line-clamp-2"
    )

    # Progreso si no está desbloqueado
    if show_progress and not is_unlocked and state:
        from ..gamification.badges import BadgeManager
        badge_mgr = BadgeManager(state)
        progress = badge_mgr.get_progress(badge.get('id'))

        if progress and isinstance(progress.get('target'), (int, float)):
            pct = progress.get('percentage', 0)
            container <= html.DIV(
                html.DIV(
                    Class="h-full bg-indigo-500 rounded-full",
                    style=f"width: {pct}%"
                ),
                Class="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden mt-2"
            )
            container <= html.P(
                f"{progress['current']}/{progress['target']}",
                Class="text-xs text-gray-500 text-center mt-1"
            )

    return container
