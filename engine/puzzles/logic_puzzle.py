# PromptCraft - Logic Puzzle Component
# Componente completo de puzzle de lógica

from browser import document, html, timer
from ..components.base import Component
from ..components.grid import MultiGrid
from ..components.hints import HintSystem, ClueList
from ..components.button import Button, button
from ..components.modal import SuccessModal
from ..components.toast import xp_toast, success
from .engine import PuzzleEngine
from .timer import PuzzleTimer


class LogicPuzzle(Component):
    """
    Componente completo de puzzle de lógica.

    Props:
        puzzle_data: Datos del puzzle
        on_complete: Callback al completar
        on_exit: Callback al salir
    """

    def __init__(self, **props):
        super().__init__(**props)
        puzzle_data = props.get('puzzle_data', {})

        self.engine = PuzzleEngine(puzzle_data)
        self.engine.on_state_change = self._on_engine_state_change
        self.engine.on_solve = self._on_puzzle_solved

        self.timer_component = None
        self.multi_grid = None
        self.hint_system = None
        self.clue_list = None

    def render(self):
        puzzle_data = self.props.get('puzzle_data', {})
        on_exit = self.props.get('on_exit')

        title = puzzle_data.get('title', 'Puzzle')
        description = puzzle_data.get('description', '')
        difficulty = puzzle_data.get('difficulty', 1)
        xp_reward = puzzle_data.get('xp_reward', 50)

        # Contenedor principal
        container = html.DIV(Class="max-w-6xl mx-auto")

        # Header
        header = self._render_header(title, difficulty, xp_reward, on_exit)
        container <= header

        # Descripción
        if description:
            container <= html.DIV(
                html.P(description, Class="text-gray-600"),
                Class="bg-white rounded-lg p-4 mb-4 border border-gray-100"
            )

        # Layout principal: Grid + Sidebar
        main_layout = html.DIV(Class="grid grid-cols-1 lg:grid-cols-3 gap-6")

        # Columna de grids (2/3)
        grid_column = html.DIV(Class="lg:col-span-2")
        grid_column <= self._render_grids()
        main_layout <= grid_column

        # Sidebar con pistas y herramientas (1/3)
        sidebar = html.DIV(Class="space-y-4")
        sidebar <= self._render_clues()
        sidebar <= self._render_hints()
        sidebar <= self._render_tools()
        main_layout <= sidebar

        container <= main_layout

        return container

    def _render_header(self, title, difficulty, xp_reward, on_exit):
        """Renderiza el header del puzzle."""
        header = html.DIV(Class="flex items-center justify-between mb-6")

        # Título y metadata
        title_section = html.DIV()
        title_section <= html.H1(title, Class="text-2xl font-bold text-gray-800")

        meta = html.DIV(Class="flex items-center gap-4 mt-2")

        # Dificultad (estrellas)
        stars = html.DIV(Class="flex items-center gap-0.5")
        for i in range(5):
            star_class = "text-yellow-400" if i < difficulty else "text-gray-300"
            stars <= html.SPAN("★", Class=f"text-sm {star_class}")
        meta <= stars

        # XP
        meta <= html.SPAN(f"+{xp_reward} XP", Class="text-sm font-medium text-indigo-600")

        title_section <= meta
        header <= title_section

        # Timer y controles
        controls = html.DIV(Class="flex items-center gap-3")

        # Timer
        self.timer_component = PuzzleTimer()
        controls <= self.timer_component.render()

        # Botón salir
        if on_exit:
            exit_btn = html.BUTTON(
                "✕ Salir",
                Class="px-3 py-1 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            )
            exit_btn.bind('click', lambda e: on_exit())
            controls <= exit_btn

        header <= controls

        return header

    def _render_grids(self):
        """Renderiza los grids del puzzle."""
        categories = self.engine.categories

        wrapper = html.DIV(Class="bg-white rounded-lg p-4 border border-gray-100")
        wrapper <= html.H3("Tabla de Eliminación", Class="font-medium text-gray-700 mb-4")

        # Crear MultiGrid
        self.multi_grid = MultiGrid(
            categories=categories,
            grid_states=self.engine.grid_states,
            on_cell_change=self._on_cell_change
        )

        wrapper <= self.multi_grid.render()

        return wrapper

    def _render_clues(self):
        """Renderiza la lista de pistas."""
        clues = self.engine.clues

        self.clue_list = ClueList(
            clues=clues,
            checked_clues=self.engine.checked_clues,
            on_clue_check=self._on_clue_check
        )

        return self.clue_list.render()

    def _render_hints(self):
        """Renderiza el sistema de hints."""
        hints = self.engine.hints

        self.hint_system = HintSystem(
            hints=hints,
            hints_used=self.engine.hints_used,
            max_hints=len(hints),
            xp_penalty=10,
            on_reveal_hint=self._on_hint_reveal
        )

        return self.hint_system.render()

    def _render_tools(self):
        """Renderiza herramientas adicionales."""
        tools = html.DIV(Class="bg-white rounded-lg p-4 border border-gray-100")
        tools <= html.H3("Herramientas", Class="font-medium text-gray-700 mb-3")

        buttons = html.DIV(Class="space-y-2")

        # Deshacer
        undo_btn = html.BUTTON(
            "↩️ Deshacer",
            Class="w-full px-3 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 rounded border border-gray-200"
        )
        undo_btn.bind('click', lambda e: self._on_undo())
        buttons <= undo_btn

        # Reiniciar
        reset_btn = html.BUTTON(
            "🔄 Reiniciar",
            Class="w-full px-3 py-2 text-sm text-left text-gray-700 hover:bg-gray-50 rounded border border-gray-200"
        )
        reset_btn.bind('click', lambda e: self._on_reset())
        buttons <= reset_btn

        # Verificar
        verify_btn = html.BUTTON(
            "✓ Verificar Solución",
            Class="w-full px-3 py-2 text-sm text-left text-white bg-indigo-600 hover:bg-indigo-700 rounded"
        )
        verify_btn.bind('click', lambda e: self._on_verify())
        buttons <= verify_btn

        tools <= buttons

        return tools

    def _on_cell_change(self, grid_key, row, col, new_state):
        """Callback cuando cambia una celda."""
        self.engine.set_cell(grid_key, row, col, new_state)

    def _on_clue_check(self, idx, is_checked):
        """Callback cuando se marca/desmarca una pista."""
        self.engine.toggle_clue(idx)

    def _on_hint_reveal(self, hint_num, hint_text):
        """Callback cuando se revela una pista."""
        self.engine.hints_used = hint_num

    def _on_undo(self):
        """Deshace el último movimiento."""
        if self.engine.undo():
            success("Movimiento deshecho")
            self._refresh_grids()

    def _on_reset(self):
        """Reinicia el puzzle."""
        self.engine.reset()
        self._refresh_grids()
        if self.timer_component:
            self.timer_component.reset()
            self.timer_component.start()
        success("Puzzle reiniciado")

    def _on_verify(self):
        """Verifica la solución actual."""
        from ..components.toast import error, success as toast_success

        if self.engine._check_solution():
            self._on_puzzle_solved({
                'time': self.engine.get_elapsed_seconds(),
                'moves': len(self.engine.moves),
                'hints_used': self.engine.hints_used
            })
        else:
            error("La solución no es correcta. ¡Sigue intentando!")

    def _refresh_grids(self):
        """Refresca los grids después de un cambio."""
        if self.multi_grid and self.multi_grid._mounted:
            self.multi_grid.grid_states = self.engine.grid_states
            self.multi_grid.update()

    def _on_engine_state_change(self, state):
        """Callback cuando cambia el estado del engine."""
        pass  # Los grids se actualizan automáticamente

    def _on_puzzle_solved(self, result):
        """Callback cuando se resuelve el puzzle."""
        # Detener timer
        if self.timer_component:
            self.timer_component.stop()

        # Calcular puntuación
        score = self.engine.calculate_score()

        # Mostrar modal de éxito
        xp_gained = score['xp']
        stars = score['stars']

        # Crear contenido del modal
        content = html.DIV(Class="text-center py-4")
        content <= html.SPAN("🎉", Class="text-6xl block mb-4")
        content <= html.P("¡Puzzle Completado!", Class="text-xl font-bold text-gray-800 mb-2")

        # Estrellas
        stars_div = html.DIV(Class="flex justify-center gap-1 mb-4")
        for i in range(3):
            star_class = "text-yellow-400 text-3xl" if i < stars else "text-gray-300 text-3xl"
            stars_div <= html.SPAN("★", Class=star_class)
        content <= stars_div

        # Stats
        stats = html.DIV(Class="grid grid-cols-3 gap-4 mb-4")

        # Tiempo
        minutes = result['time'] // 60
        seconds = result['time'] % 60
        stats <= html.DIV(
            html.P(f"{minutes}:{seconds:02d}", Class="text-2xl font-bold text-gray-800") +
            html.P("Tiempo", Class="text-sm text-gray-500")
        )

        # Movimientos
        stats <= html.DIV(
            html.P(str(result['moves']), Class="text-2xl font-bold text-gray-800") +
            html.P("Movimientos", Class="text-sm text-gray-500")
        )

        # Pistas
        stats <= html.DIV(
            html.P(str(result['hints_used']), Class="text-2xl font-bold text-gray-800") +
            html.P("Pistas", Class="text-sm text-gray-500")
        )

        content <= stats

        # XP ganado
        content <= html.DIV(
            html.SPAN(f"+{xp_gained}", Class="text-3xl font-bold text-indigo-600") +
            html.SPAN(" XP", Class="text-xl text-gray-500"),
            Class="mb-4"
        )

        # Notificar completación
        on_complete = self.props.get('on_complete')
        if on_complete:
            on_complete({
                'puzzle_id': self.props.get('puzzle_data', {}).get('id'),
                'xp': xp_gained,
                'stars': stars,
                'time': result['time'],
                'moves': result['moves'],
                'hints_used': result['hints_used']
            })

        # Mostrar modal
        modal = SuccessModal(
            title="¡Felicitaciones!",
            message="¡Has resuelto el puzzle!",
            xp_gained=xp_gained
        )
        modal.props['content'] = content
        modal.show()

    def on_mount(self):
        """Al montar, iniciar el puzzle."""
        self.engine.start()
        if self.timer_component:
            self.timer_component.start()

    def on_unmount(self):
        """Al desmontar, detener timer."""
        if self.timer_component:
            self.timer_component.stop()
