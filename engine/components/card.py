# PromptCraft - Card Components
# Tarjetas para mostrar contenido

from browser import html
from .base import Component, icon


class Card(Component):
    """
    Componente de tarjeta genérica.

    Props:
        title: Título de la tarjeta
        subtitle: Subtítulo opcional
        content: Contenido (string o elemento DOM)
        footer: Contenido del footer
        padding: bool - Si aplicar padding interno
        hover: bool - Efecto hover
        on_click: Callback al hacer clic
    """

    def render(self):
        title = self.props.get('title')
        subtitle = self.props.get('subtitle')
        content = self.props.get('content')
        footer = self.props.get('footer')
        padding = self.props.get('padding', True)
        hover = self.props.get('hover', False)
        on_click = self.props.get('on_click')
        extra_class = self.props.get('class', '')

        # Clases base
        base_classes = "bg-white rounded-xl shadow-sm border border-gray-100"
        hover_classes = "hover:shadow-md hover:border-gray-200 transition-all cursor-pointer" if hover else ""
        padding_classes = "p-6" if padding else ""

        card = html.DIV(Class=f"{base_classes} {hover_classes} {extra_class}")

        # Header
        if title or subtitle:
            header = html.DIV(Class=f"{'px-6 pt-6' if not padding else ''}")
            if title:
                header <= html.H3(title, Class="text-lg font-semibold text-gray-800")
            if subtitle:
                header <= html.P(subtitle, Class="text-sm text-gray-500 mt-1")
            card <= header

        # Content
        if content:
            content_div = html.DIV(Class=f"{padding_classes} {'pt-4' if title else ''}")
            if isinstance(content, str):
                content_div <= html.P(content)
            else:
                content_div <= content
            card <= content_div

        # Footer
        if footer:
            footer_div = html.DIV(
                Class=f"{'px-6 pb-6' if not padding else 'pt-4 border-t border-gray-100 mt-4'}"
            )
            if isinstance(footer, str):
                footer_div <= html.P(footer, Class="text-sm text-gray-500")
            else:
                footer_div <= footer
            card <= footer_div

        if on_click:
            card.bind('click', on_click)

        return card


class LessonCard(Component):
    """
    Tarjeta para mostrar una lección.

    Props:
        lesson: Dict con datos de la lección
            - id: ID de la lección
            - title: Título
            - description: Descripción
            - category: Categoría
            - difficulty: 'beginner' | 'intermediate' | 'advanced'
            - duration: Duración estimada
            - completed: bool
            - locked: bool
        on_click: Callback al hacer clic
    """

    DIFFICULTY_COLORS = {
        'beginner': 'bg-green-100 text-green-700',
        'intermediate': 'bg-yellow-100 text-yellow-700',
        'advanced': 'bg-red-100 text-red-700',
    }

    DIFFICULTY_LABELS = {
        'beginner': 'Principiante',
        'intermediate': 'Intermedio',
        'advanced': 'Avanzado',
    }

    CATEGORY_ICONS = {
        'fundamentos': '📚',
        'tecnicas': '🎯',
        'avanzado': '🚀',
        'casos': '💼',
    }

    def render(self):
        lesson = self.props.get('lesson', {})
        on_click = self.props.get('on_click')

        lesson_id = lesson.get('id', '')
        title = lesson.get('title', 'Sin título')
        description = lesson.get('description', '')
        category = lesson.get('category', 'fundamentos')
        difficulty = lesson.get('difficulty', 'beginner')
        duration = lesson.get('duration', '10 min')
        completed = lesson.get('completed', False)
        locked = lesson.get('locked', False)

        # Clases base
        base_classes = "bg-white rounded-xl border border-gray-100 overflow-hidden transition-all"
        if locked:
            state_classes = "opacity-60"
        elif completed:
            state_classes = "border-green-200 bg-green-50/30"
        else:
            state_classes = "hover:shadow-md hover:border-indigo-200 cursor-pointer"

        card = html.DIV(Class=f"{base_classes} {state_classes}")

        # Header con categoría y estado
        header = html.DIV(Class="px-5 py-3 border-b border-gray-50 flex items-center justify-between")

        # Categoría
        cat_icon = self.CATEGORY_ICONS.get(category, '📖')
        header <= html.SPAN(
            f"{cat_icon} {category.capitalize()}",
            Class="text-sm text-gray-500"
        )

        # Estado (completado/bloqueado)
        if completed:
            header <= html.SPAN(
                icon('check', 'w-4 h-4 mr-1') + "Completada",
                Class="flex items-center text-sm text-green-600 font-medium"
            )
        elif locked:
            header <= html.SPAN(
                icon('lock', 'w-4 h-4 mr-1') + "Bloqueada",
                Class="flex items-center text-sm text-gray-400"
            )

        card <= header

        # Contenido
        content = html.DIV(Class="p-5")

        # Título
        content <= html.H3(title, Class="text-lg font-semibold text-gray-800")

        # Descripción
        content <= html.P(
            description[:100] + ('...' if len(description) > 100 else ''),
            Class="text-gray-600 mt-2 text-sm"
        )

        # Footer con metadata
        meta = html.DIV(Class="flex items-center gap-4 mt-4")

        # Dificultad
        diff_classes = self.DIFFICULTY_COLORS.get(difficulty, 'bg-gray-100 text-gray-700')
        meta <= html.SPAN(
            self.DIFFICULTY_LABELS.get(difficulty, difficulty),
            Class=f"text-xs px-2 py-1 rounded-full {diff_classes}"
        )

        # Duración
        meta <= html.SPAN(
            f"⏱️ {duration}",
            Class="text-xs text-gray-500"
        )

        content <= meta
        card <= content

        # Bind click si no está bloqueada
        if on_click and not locked:
            card.bind('click', lambda e: on_click(lesson_id))

        return card


class PuzzleCard(Component):
    """
    Tarjeta para mostrar un puzzle.

    Props:
        puzzle: Dict con datos del puzzle
            - id: ID del puzzle
            - title: Título
            - description: Descripción
            - difficulty: 1-5
            - xp_reward: XP que otorga
            - solved: bool
            - best_time: Mejor tiempo (opcional)
        on_click: Callback al hacer clic
    """

    def render(self):
        puzzle = self.props.get('puzzle', {})
        on_click = self.props.get('on_click')

        puzzle_id = puzzle.get('id', '')
        title = puzzle.get('title', 'Puzzle')
        description = puzzle.get('description', '')
        difficulty = puzzle.get('difficulty', 1)
        xp_reward = puzzle.get('xp_reward', 50)
        solved = puzzle.get('solved', False)
        best_time = puzzle.get('best_time')

        # Clases base
        base_classes = "bg-white rounded-xl border overflow-hidden transition-all hover:shadow-md cursor-pointer"
        border_class = "border-green-200" if solved else "border-gray-100 hover:border-indigo-200"

        card = html.DIV(Class=f"{base_classes} {border_class}")

        # Header con dificultad visual
        header = html.DIV(Class="px-5 py-3 border-b border-gray-50 flex items-center justify-between")

        # Estrellas de dificultad
        stars = html.DIV(Class="flex items-center gap-0.5")
        for i in range(5):
            star_class = "text-yellow-400" if i < difficulty else "text-gray-200"
            stars <= html.SPAN("★", Class=f"text-sm {star_class}")
        header <= stars

        # XP reward
        header <= html.SPAN(
            f"+{xp_reward} XP",
            Class="text-sm font-medium text-indigo-600"
        )

        card <= header

        # Contenido
        content = html.DIV(Class="p-5")

        # Ícono y título
        title_row = html.DIV(Class="flex items-center gap-3")
        puzzle_emoji = "✅" if solved else "🧩"
        title_row <= html.SPAN(puzzle_emoji, Class="text-2xl")
        title_row <= html.H3(title, Class="text-lg font-semibold text-gray-800")
        content <= title_row

        # Descripción
        content <= html.P(
            description[:80] + ('...' if len(description) > 80 else ''),
            Class="text-gray-600 mt-2 text-sm"
        )

        # Mejor tiempo si está resuelto
        if solved and best_time:
            content <= html.DIV(
                html.SPAN("🏆 Mejor tiempo: ", Class="text-gray-500") +
                html.SPAN(best_time, Class="font-medium text-gray-700"),
                Class="mt-3 text-sm"
            )

        card <= content

        if on_click:
            card.bind('click', lambda e: on_click(puzzle_id))

        return card


def card(**props):
    """Helper para crear tarjetas rápidamente."""
    return Card(**props).render()


def lesson_card(lesson, on_click=None):
    """Helper para crear tarjetas de lección."""
    return LessonCard(lesson=lesson, on_click=on_click).render()


def puzzle_card(puzzle, on_click=None):
    """Helper para crear tarjetas de puzzle."""
    return PuzzleCard(puzzle=puzzle, on_click=on_click).render()
