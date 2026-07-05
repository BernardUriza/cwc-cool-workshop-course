# PromptCraft - Badge Display Components
# Componentes para mostrar badges y logros

from browser import html
from .base import Component


class BadgeDisplay(Component):
    """
    Muestra un badge individual.

    Props:
        badge: Dict con datos del badge
            - id: ID del badge
            - name: Nombre
            - description: Descripción
            - icon: Emoji del badge
            - rarity: 'common' | 'rare' | 'epic' | 'legendary'
            - unlocked: bool
            - unlocked_at: Fecha de desbloqueo
        size: 'sm' | 'md' | 'lg'
        show_tooltip: Mostrar tooltip con descripción
    """

    RARITY_COLORS = {
        'common': {
            'bg': 'bg-gray-100',
            'border': 'border-gray-300',
            'text': 'text-gray-600',
            'glow': '',
        },
        'rare': {
            'bg': 'bg-blue-100',
            'border': 'border-blue-400',
            'text': 'text-blue-700',
            'glow': 'ring-2 ring-blue-200',
        },
        'epic': {
            'bg': 'bg-purple-100',
            'border': 'border-purple-400',
            'text': 'text-purple-700',
            'glow': 'ring-2 ring-purple-200',
        },
        'legendary': {
            'bg': 'bg-gradient-to-br from-yellow-100 to-amber-200',
            'border': 'border-yellow-400',
            'text': 'text-amber-700',
            'glow': 'ring-2 ring-yellow-300 shadow-lg shadow-yellow-200',
        },
    }

    RARITY_LABELS = {
        'common': 'Común',
        'rare': 'Raro',
        'epic': 'Épico',
        'legendary': 'Legendario',
    }

    SIZES = {
        'sm': {'container': 'w-12 h-12', 'icon': 'text-xl', 'padding': 'p-2'},
        'md': {'container': 'w-16 h-16', 'icon': 'text-2xl', 'padding': 'p-3'},
        'lg': {'container': 'w-24 h-24', 'icon': 'text-4xl', 'padding': 'p-4'},
    }

    def render(self):
        badge = self.props.get('badge', {})
        size = self.props.get('size', 'md')
        show_tooltip = self.props.get('show_tooltip', True)
        on_click = self.props.get('on_click')

        badge_id = badge.get('id', '')
        name = badge.get('name', 'Badge')
        description = badge.get('description', '')
        badge_icon = badge.get('icon', '🏆')
        rarity = badge.get('rarity', 'common')
        unlocked = badge.get('unlocked', False)

        size_config = self.SIZES.get(size, self.SIZES['md'])
        rarity_config = self.RARITY_COLORS.get(rarity, self.RARITY_COLORS['common'])

        # Container
        container = html.DIV(Class="inline-flex flex-col items-center group relative")

        # Badge circle
        if unlocked:
            badge_classes = f"{size_config['container']} {size_config['padding']} rounded-full {rarity_config['bg']} border-2 {rarity_config['border']} {rarity_config['glow']} flex items-center justify-center"
        else:
            badge_classes = f"{size_config['container']} {size_config['padding']} rounded-full bg-gray-200 border-2 border-gray-300 flex items-center justify-center opacity-50"

        badge_elem = html.DIV(
            html.SPAN(badge_icon if unlocked else '🔒', Class=size_config['icon']),
            Class=badge_classes
        )

        if on_click:
            badge_elem.Class += " cursor-pointer hover:scale-110 transition-transform"
            badge_elem.bind('click', lambda e: on_click(badge_id))

        container <= badge_elem

        # Nombre debajo (solo en tamaños md y lg)
        if size in ['md', 'lg']:
            name_class = "text-xs mt-1 text-center max-w-[80px] truncate"
            if unlocked:
                name_class += f" {rarity_config['text']} font-medium"
            else:
                name_class += " text-gray-400"

            container <= html.SPAN(name, Class=name_class, title=name)

        # Tooltip
        if show_tooltip:
            tooltip = html.DIV(
                Class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-10"
            )
            tooltip <= html.P(name, Class="font-medium")
            tooltip <= html.P(description, Class="text-gray-300 max-w-[200px] whitespace-normal")

            if unlocked:
                tooltip <= html.P(
                    f"Rareza: {self.RARITY_LABELS.get(rarity, rarity)}",
                    Class=f"mt-1 {rarity_config['text']}"
                )
            else:
                tooltip <= html.P("🔒 No desbloqueado", Class="mt-1 text-gray-400")

            # Arrow
            tooltip <= html.DIV(
                Class="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900"
            )

            container <= tooltip

        return container


class BadgeGrid(Component):
    """
    Grid de badges.

    Props:
        badges: Lista de badges
        columns: Número de columnas
        size: Tamaño de los badges
        show_locked: Mostrar badges bloqueados
        on_badge_click: Callback al hacer clic en un badge
    """

    def render(self):
        badges = self.props.get('badges', [])
        columns = self.props.get('columns', 5)
        size = self.props.get('size', 'md')
        show_locked = self.props.get('show_locked', True)
        on_badge_click = self.props.get('on_badge_click')
        filter_rarity = self.props.get('filter_rarity')

        # Filtrar badges
        filtered_badges = badges
        if not show_locked:
            filtered_badges = [b for b in badges if b.get('unlocked', False)]
        if filter_rarity:
            filtered_badges = [b for b in filtered_badges if b.get('rarity') == filter_rarity]

        # Grid container
        grid = html.DIV(
            Class=f"grid gap-4",
            style=f"grid-template-columns: repeat({columns}, minmax(0, 1fr));"
        )

        for badge in filtered_badges:
            badge_elem = BadgeDisplay(
                badge=badge,
                size=size,
                on_click=on_badge_click
            ).render()
            grid <= badge_elem

        if len(filtered_badges) == 0:
            empty = html.DIV(
                html.SPAN("🏆", Class="text-4xl text-gray-300") +
                html.P("No hay badges para mostrar", Class="text-gray-400 mt-2"),
                Class="col-span-full text-center py-8"
            )
            grid <= empty

        return grid


class BadgeProgress(Component):
    """
    Muestra el progreso hacia un badge.

    Props:
        badge: Datos del badge
        current: Valor actual
        target: Valor objetivo
    """

    def render(self):
        badge = self.props.get('badge', {})
        current = self.props.get('current', 0)
        target = self.props.get('target', 1)

        name = badge.get('name', 'Badge')
        badge_icon = badge.get('icon', '🏆')
        description = badge.get('description', '')

        progress = min(100, (current / target) * 100) if target > 0 else 0
        is_complete = current >= target

        container = html.DIV(
            Class="flex items-center gap-4 p-3 bg-white rounded-lg border border-gray-100"
        )

        # Badge icon
        icon_bg = "bg-green-100" if is_complete else "bg-gray-100"
        icon_wrapper = html.DIV(
            html.SPAN(badge_icon, Class="text-2xl"),
            Class=f"w-12 h-12 rounded-full flex items-center justify-center {icon_bg}"
        )
        container <= icon_wrapper

        # Info and progress
        info = html.DIV(Class="flex-1")
        info <= html.P(name, Class="font-medium text-gray-800")
        info <= html.P(description, Class="text-sm text-gray-500")

        # Progress bar
        progress_bar = html.DIV(Class="mt-2 flex items-center gap-2")
        bar_color = "bg-green-500" if is_complete else "bg-indigo-500"
        progress_bar <= html.DIV(
            html.DIV(
                Class=f"h-full rounded-full transition-all {bar_color}",
                style=f"width: {progress}%"
            ),
            Class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden"
        )
        progress_bar <= html.SPAN(
            f"{current}/{target}",
            Class="text-xs text-gray-500 font-medium min-w-[40px] text-right"
        )

        info <= progress_bar
        container <= info

        # Complete indicator
        if is_complete:
            container <= html.SPAN("✓", Class="text-green-500 text-xl font-bold")

        return container


def badge_display(badge, **props):
    """Helper para crear display de badge."""
    return BadgeDisplay(badge=badge, **props).render()


def badge_grid(badges, **props):
    """Helper para crear grid de badges."""
    return BadgeGrid(badges=badges, **props).render()


def badge_progress(badge, current, target, **props):
    """Helper para crear progreso de badge."""
    return BadgeProgress(badge=badge, current=current, target=target, **props).render()
