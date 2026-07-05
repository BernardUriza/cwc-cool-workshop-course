# PromptCraft - Hints System Component
# Sistema de pistas para puzzles

from browser import html
from .base import Component, icon
from .button import Button


class HintSystem(Component):
    """
    Sistema de pistas progresivo para puzzles.

    Props:
        hints: Lista de pistas ordenadas de menor a mayor revelación
        hints_used: Número de pistas ya usadas
        max_hints: Máximo de pistas disponibles
        xp_penalty: XP que se pierde por pista
        on_reveal_hint: Callback al revelar una pista
    """

    def __init__(self, **props):
        super().__init__(**props)
        self.revealed_hints = props.get('hints_used', 0)

    def render(self):
        hints = self.props.get('hints', [])
        max_hints = self.props.get('max_hints', len(hints))
        xp_penalty = self.props.get('xp_penalty', 10)
        on_reveal_hint = self.props.get('on_reveal_hint')

        container = html.DIV(Class="bg-amber-50 rounded-lg border border-amber-200 p-4")

        # Header
        header = html.DIV(Class="flex items-center justify-between mb-3")
        header <= html.DIV(
            html.SPAN("💡", Class="text-xl mr-2") +
            html.SPAN("Pistas", Class="font-medium text-amber-800"),
            Class="flex items-center"
        )

        # Contador de pistas
        hints_left = max_hints - self.revealed_hints
        header <= html.SPAN(
            f"{hints_left} disponibles",
            Class="text-sm text-amber-600"
        )

        container <= header

        # Pistas reveladas
        if self.revealed_hints > 0:
            revealed_section = html.DIV(Class="space-y-2 mb-3")
            for i in range(self.revealed_hints):
                if i < len(hints):
                    hint_div = html.DIV(
                        html.SPAN(f"#{i+1}: ", Class="font-medium text-amber-700") +
                        html.SPAN(hints[i], Class="text-amber-900"),
                        Class="p-2 bg-white rounded border border-amber-100 text-sm"
                    )
                    revealed_section <= hint_div
            container <= revealed_section

        # Botón para revelar siguiente pista
        if self.revealed_hints < max_hints and self.revealed_hints < len(hints):
            reveal_section = html.DIV(Class="flex items-center justify-between p-2 bg-amber-100 rounded")

            info = html.DIV(Class="text-sm text-amber-700")
            info <= html.SPAN("¿Necesitas ayuda? ")
            info <= html.SPAN(f"(-{xp_penalty} XP)", Class="text-amber-600 font-medium")

            reveal_btn = html.BUTTON(
                "Ver pista",
                Class="px-3 py-1 text-sm bg-amber-500 text-white rounded hover:bg-amber-600 transition-colors"
            )
            reveal_btn.bind('click', lambda e: self._reveal_next_hint(hints, on_reveal_hint))

            reveal_section <= info
            reveal_section <= reveal_btn
            container <= reveal_section
        elif self.revealed_hints >= len(hints):
            container <= html.P(
                "No hay más pistas disponibles",
                Class="text-sm text-amber-600 italic"
            )

        return container

    def _reveal_next_hint(self, hints, callback):
        """Revela la siguiente pista."""
        if self.revealed_hints < len(hints):
            self.revealed_hints += 1

            if callback:
                callback(self.revealed_hints, hints[self.revealed_hints - 1])

            # Re-render
            if self._mounted and self.element:
                parent = self.element.parentNode
                self.unmount()
                self.mount(parent)

    def get_revealed_count(self):
        """Obtiene el número de pistas reveladas."""
        return self.revealed_hints

    def reset(self):
        """Reinicia las pistas."""
        self.revealed_hints = 0
        if self._mounted:
            self.update()


class ClueList(Component):
    """
    Lista de pistas/reglas del puzzle.

    Props:
        clues: Lista de pistas del puzzle
        checked_clues: Set de índices de pistas verificadas
        on_clue_check: Callback al marcar una pista
    """

    def __init__(self, **props):
        super().__init__(**props)
        self.checked_clues = set(props.get('checked_clues', []))

    def render(self):
        clues = self.props.get('clues', [])
        on_clue_check = self.props.get('on_clue_check')

        container = html.DIV(Class="bg-white rounded-lg border border-gray-200 p-4")

        # Header
        container <= html.H3(
            "📋 Pistas del Puzzle",
            Class="font-medium text-gray-800 mb-3"
        )

        # Lista de pistas
        clue_list = html.UL(Class="space-y-2")

        for idx, clue in enumerate(clues):
            is_checked = idx in self.checked_clues

            clue_item = html.LI(
                Class="flex items-start gap-2 p-2 rounded hover:bg-gray-50 cursor-pointer transition-colors"
            )

            # Checkbox
            checkbox_colors = "bg-green-500 border-green-500" if is_checked else "border-gray-300 bg-white"
            checkbox = html.DIV(
                html.SPAN("✓" if is_checked else "", Class="text-white text-xs"),
                Class=f"w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors {checkbox_colors}"
            )

            # Texto de la pista
            text_class = "text-gray-400 line-through" if is_checked else "text-gray-700"
            clue_text = html.SPAN(
                f"{idx + 1}. {clue}",
                Class=f"text-sm {text_class}"
            )

            clue_item <= checkbox
            clue_item <= clue_text

            def make_handler(i):
                def handler(e):
                    self._toggle_clue(i, on_clue_check)
                return handler

            clue_item.bind('click', make_handler(idx))
            clue_list <= clue_item

        container <= clue_list

        # Progreso
        progress = len(self.checked_clues)
        total = len(clues)
        container <= html.DIV(
            html.SPAN(f"Progreso: {progress}/{total} pistas verificadas"),
            Class="mt-3 text-sm text-gray-500 text-center"
        )

        return container

    def _toggle_clue(self, idx, callback):
        """Alterna el estado de una pista."""
        if idx in self.checked_clues:
            self.checked_clues.remove(idx)
        else:
            self.checked_clues.add(idx)

        if callback:
            callback(idx, idx in self.checked_clues)

        # Re-render
        if self._mounted and self.element:
            parent = self.element.parentNode
            self.unmount()
            self.mount(parent)

    def get_checked(self):
        """Obtiene las pistas marcadas."""
        return set(self.checked_clues)

    def clear(self):
        """Limpia todas las pistas marcadas."""
        self.checked_clues = set()
        if self._mounted:
            self.update()


def hint_system(**props):
    """Helper para crear sistema de pistas."""
    return HintSystem(**props)


def clue_list(**props):
    """Helper para crear lista de pistas."""
    return ClueList(**props)
