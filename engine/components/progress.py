# PromptCraft - Progress Components
# Barras de progreso, XP y nivel

from browser import html
from .base import Component


class ProgressBar(Component):
    """
    Barra de progreso genérica.

    Props:
        value: Valor actual (0-100)
        max_value: Valor máximo (default 100)
        color: Color de la barra ('indigo', 'green', 'yellow', 'red')
        size: 'sm' | 'md' | 'lg'
        show_label: Mostrar porcentaje
        animated: Animación de la barra
    """

    COLORS = {
        'indigo': 'bg-indigo-500',
        'green': 'bg-green-500',
        'yellow': 'bg-yellow-500',
        'red': 'bg-red-500',
        'blue': 'bg-blue-500',
        'purple': 'bg-purple-500',
        'gradient': 'bg-gradient-to-r from-indigo-500 to-purple-500',
    }

    SIZES = {
        'sm': 'h-1.5',
        'md': 'h-2.5',
        'lg': 'h-4',
    }

    def render(self):
        value = self.props.get('value', 0)
        max_value = self.props.get('max_value', 100)
        color = self.props.get('color', 'indigo')
        size = self.props.get('size', 'md')
        show_label = self.props.get('show_label', False)
        animated = self.props.get('animated', True)
        label = self.props.get('label', '')

        # Calcular porcentaje
        percentage = min(100, max(0, (value / max_value) * 100)) if max_value > 0 else 0

        # Contenedor
        container = html.DIV(Class="w-full")

        # Label superior
        if label or show_label:
            label_row = html.DIV(Class="flex justify-between mb-1 text-sm")
            if label:
                label_row <= html.SPAN(label, Class="text-gray-600")
            if show_label:
                label_row <= html.SPAN(f"{int(percentage)}%", Class="text-gray-500 font-medium")
            container <= label_row

        # Barra
        size_class = self.SIZES.get(size, self.SIZES['md'])
        color_class = self.COLORS.get(color, self.COLORS['indigo'])
        animation_class = "transition-all duration-500" if animated else ""

        bar_container = html.DIV(
            Class=f"w-full bg-gray-200 rounded-full overflow-hidden {size_class}"
        )

        bar_fill = html.DIV(
            Class=f"{color_class} {size_class} rounded-full {animation_class}",
            style=f"width: {percentage}%"
        )

        bar_container <= bar_fill
        container <= bar_container

        return container


class XPBar(Component):
    """
    Barra de experiencia con información de nivel.

    Props:
        current_xp: XP actual
        level_info: Dict con info del nivel (from state.get_level_info())
        compact: Modo compacto
    """

    def render(self):
        current_xp = self.props.get('current_xp', 0)
        level_info = self.props.get('level_info', {})
        compact = self.props.get('compact', False)

        level = level_info.get('level', 1)
        title = level_info.get('title', 'Novato')
        progress = level_info.get('progress', 0)
        xp_in_level = level_info.get('xp_in_level', 0)
        xp_for_next = level_info.get('xp_for_next', 100)

        if compact:
            # Versión compacta
            container = html.DIV(Class="flex items-center gap-3")

            # Nivel badge
            container <= html.DIV(
                html.SPAN(str(level), Class="text-lg font-bold text-white"),
                Class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center"
            )

            # Barra
            bar_container = html.DIV(Class="flex-1")
            bar_container <= html.DIV(
                html.DIV(
                    Class="h-full bg-indigo-500 rounded-full transition-all duration-500",
                    style=f"width: {progress}%"
                ),
                Class="w-full h-2 bg-gray-200 rounded-full overflow-hidden"
            )
            container <= bar_container

            # XP
            container <= html.SPAN(f"{current_xp} XP", Class="text-sm text-gray-600 font-medium")

            return container

        # Versión completa
        container = html.DIV(Class="bg-white rounded-xl p-4 border border-gray-100")

        # Header
        header = html.DIV(Class="flex items-center justify-between mb-3")
        header <= html.DIV(
            html.SPAN(f"Nivel {level}", Class="text-lg font-bold text-gray-800") +
            html.SPAN(f" - {title}", Class="text-gray-500"),
            Class="flex items-center"
        )
        header <= html.SPAN(f"{current_xp} XP total", Class="text-sm text-indigo-600 font-medium")
        container <= header

        # Barra de progreso
        bar_section = html.DIV()
        bar_section <= html.DIV(
            html.DIV(
                Class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500",
                style=f"width: {progress}%"
            ),
            Class="w-full h-3 bg-gray-200 rounded-full overflow-hidden"
        )

        # Info bajo la barra
        bar_info = html.DIV(Class="flex justify-between mt-2 text-sm")
        bar_info <= html.SPAN(f"{xp_in_level} XP", Class="text-gray-500")
        bar_info <= html.SPAN(f"{xp_for_next} XP para nivel {level + 1}", Class="text-gray-500")
        bar_section <= bar_info

        container <= bar_section

        return container


class LevelBadge(Component):
    """
    Badge que muestra el nivel del usuario.

    Props:
        level: Número de nivel
        title: Título del nivel
        size: 'sm' | 'md' | 'lg'
    """

    LEVEL_COLORS = {
        1: 'from-gray-400 to-gray-500',      # Novato
        2: 'from-green-400 to-green-600',     # Aprendiz
        3: 'from-blue-400 to-blue-600',       # Estudiante
        4: 'from-purple-400 to-purple-600',   # Practicante
        5: 'from-yellow-400 to-yellow-600',   # Competente
        6: 'from-orange-400 to-orange-600',   # Hábil
        7: 'from-red-400 to-red-600',         # Experto
        8: 'from-pink-400 to-pink-600',       # Maestro
        9: 'from-indigo-400 to-indigo-600',   # Gran Maestro
        10: 'from-yellow-300 via-yellow-500 to-amber-600',  # Leyenda
    }

    SIZES = {
        'sm': {'badge': 'w-8 h-8', 'text': 'text-sm'},
        'md': {'badge': 'w-12 h-12', 'text': 'text-lg'},
        'lg': {'badge': 'w-16 h-16', 'text': 'text-2xl'},
    }

    def render(self):
        level = self.props.get('level', 1)
        title = self.props.get('title', '')
        size = self.props.get('size', 'md')
        show_title = self.props.get('show_title', True)

        size_config = self.SIZES.get(size, self.SIZES['md'])
        gradient = self.LEVEL_COLORS.get(level, self.LEVEL_COLORS[1])

        container = html.DIV(Class="flex flex-col items-center")

        # Badge circular
        badge = html.DIV(
            html.SPAN(str(level), Class=f"{size_config['text']} font-bold text-white"),
            Class=f"{size_config['badge']} rounded-full bg-gradient-to-br {gradient} flex items-center justify-center shadow-lg"
        )
        container <= badge

        # Título
        if show_title and title:
            container <= html.SPAN(title, Class="text-sm text-gray-600 mt-1")

        return container


def progress_bar(value, **props):
    """Helper para crear barras de progreso."""
    return ProgressBar(value=value, **props).render()


def xp_bar(current_xp, level_info, **props):
    """Helper para crear barras de XP."""
    return XPBar(current_xp=current_xp, level_info=level_info, **props).render()


def level_badge(level, **props):
    """Helper para crear badges de nivel."""
    return LevelBadge(level=level, **props).render()
