# PromptCraft - Puzzle Engine
# Motor principal para manejar puzzles

from browser import timer


class PuzzleEngine:
    """
    Motor de puzzles que coordina la lógica del juego.
    """

    def __init__(self, puzzle_data):
        """
        Inicializa el motor con datos del puzzle.

        Args:
            puzzle_data: Dict con la definición del puzzle
        """
        self.puzzle_data = puzzle_data
        self.categories = puzzle_data.get('categories', [])
        self.clues = puzzle_data.get('clues', [])
        self.solution = puzzle_data.get('solution', {})
        self.hints = puzzle_data.get('hints', [])

        # Estado del juego
        self.grid_states = {}  # {grid_key: {(row, col): state}}
        self.checked_clues = set()
        self.hints_used = 0
        self.is_solved = False
        self.start_time = None
        self.elapsed_time = 0
        self.moves = []  # Historial de movimientos

        # Callbacks
        self.on_state_change = None
        self.on_solve = None
        self.on_hint_used = None

        self._init_grids()

    def _init_grids(self):
        """Inicializa los grids vacíos."""
        for i in range(len(self.categories)):
            for j in range(i + 1, len(self.categories)):
                cat1 = self.categories[i]
                cat2 = self.categories[j]
                grid_key = f"{cat1['name']}__{cat2['name']}"
                self.grid_states[grid_key] = {}

    def start(self):
        """Inicia el puzzle (timer)."""
        from browser import window
        self.start_time = window.Date.now()
        return self

    def get_elapsed_seconds(self):
        """Obtiene el tiempo transcurrido en segundos."""
        if not self.start_time:
            return 0
        from browser import window
        return int((window.Date.now() - self.start_time) / 1000)

    def set_cell(self, grid_key, row, col, state):
        """
        Establece el estado de una celda.

        Args:
            grid_key: Clave del grid (e.g., "Personas__Técnicas")
            row: Índice de fila
            col: Índice de columna
            state: 'empty' | 'check' | 'x'
        """
        if self.is_solved:
            return

        if grid_key not in self.grid_states:
            self.grid_states[grid_key] = {}

        old_state = self.grid_states[grid_key].get((row, col), 'empty')
        self.grid_states[grid_key][(row, col)] = state

        # Registrar movimiento
        self.moves.append({
            'grid': grid_key,
            'row': row,
            'col': col,
            'from': old_state,
            'to': state,
            'time': self.get_elapsed_seconds()
        })

        # Auto-eliminación si es check
        if state == 'check':
            self._auto_eliminate(grid_key, row, col)

        # Notificar cambio
        if self.on_state_change:
            self.on_state_change(self.get_state())

        # Verificar si se resolvió
        if self._check_solution():
            self._on_puzzle_solved()

    def _auto_eliminate(self, grid_key, row, col):
        """
        Auto-elimina celdas cuando se marca un check.
        """
        cat_names = grid_key.split('__')
        cat1 = next((c for c in self.categories if c['name'] == cat_names[0]), None)
        cat2 = next((c for c in self.categories if c['name'] == cat_names[1]), None)

        if not cat1 or not cat2:
            return

        grid_state = self.grid_states[grid_key]

        # Marcar X en el resto de la fila
        for c in range(len(cat2['items'])):
            if c != col:
                key = (row, c)
                if grid_state.get(key, 'empty') == 'empty':
                    grid_state[key] = 'x'

        # Marcar X en el resto de la columna
        for r in range(len(cat1['items'])):
            if r != row:
                key = (r, col)
                if grid_state.get(key, 'empty') == 'empty':
                    grid_state[key] = 'x'

    def _check_solution(self):
        """
        Verifica si el puzzle está resuelto correctamente.
        """
        for grid_key, expected_grid in self.solution.items():
            actual_grid = self.grid_states.get(grid_key, {})

            # Verificar que todos los checks esperados estén presentes
            for key_str, expected_state in expected_grid.items():
                if expected_state == 'check':
                    # Parsear la key (viene como string del JSON)
                    if isinstance(key_str, str):
                        row, col = map(int, key_str.split(','))
                        key = (row, col)
                    else:
                        key = key_str

                    if actual_grid.get(key) != 'check':
                        return False

        return True

    def _on_puzzle_solved(self):
        """Callback cuando el puzzle se resuelve."""
        self.is_solved = True
        self.elapsed_time = self.get_elapsed_seconds()

        if self.on_solve:
            self.on_solve({
                'time': self.elapsed_time,
                'moves': len(self.moves),
                'hints_used': self.hints_used
            })

    def use_hint(self):
        """
        Usa una pista si está disponible.

        Returns:
            La pista o None si no hay más
        """
        if self.hints_used >= len(self.hints):
            return None

        hint = self.hints[self.hints_used]
        self.hints_used += 1

        if self.on_hint_used:
            self.on_hint_used(self.hints_used, hint)

        return hint

    def toggle_clue(self, clue_idx):
        """Marca/desmarca una pista como verificada."""
        if clue_idx in self.checked_clues:
            self.checked_clues.remove(clue_idx)
        else:
            self.checked_clues.add(clue_idx)

    def undo(self):
        """Deshace el último movimiento."""
        if not self.moves:
            return False

        move = self.moves.pop()
        self.grid_states[move['grid']][(move['row'], move['col'])] = move['from']

        if self.on_state_change:
            self.on_state_change(self.get_state())

        return True

    def reset(self):
        """Reinicia el puzzle completamente."""
        self._init_grids()
        self.checked_clues = set()
        self.hints_used = 0
        self.is_solved = False
        self.moves = []
        self.start()

        if self.on_state_change:
            self.on_state_change(self.get_state())

    def get_state(self):
        """Obtiene el estado actual del puzzle."""
        return {
            'grid_states': dict(self.grid_states),
            'checked_clues': list(self.checked_clues),
            'hints_used': self.hints_used,
            'is_solved': self.is_solved,
            'elapsed_time': self.get_elapsed_seconds(),
            'moves_count': len(self.moves),
        }

    def load_state(self, state):
        """Carga un estado guardado."""
        self.grid_states = state.get('grid_states', {})
        self.checked_clues = set(state.get('checked_clues', []))
        self.hints_used = state.get('hints_used', 0)
        self.is_solved = state.get('is_solved', False)

    def calculate_score(self):
        """
        Calcula la puntuación basada en el desempeño.

        Returns:
            Dict con score, xp, y detalles
        """
        if not self.is_solved:
            return {'score': 0, 'xp': 0, 'details': {}}

        base_xp = self.puzzle_data.get('xp_reward', 50)
        difficulty = self.puzzle_data.get('difficulty', 1)

        # Bonificaciones
        time_bonus = 0
        par_time = self.puzzle_data.get('par_time', 300)  # 5 minutos por defecto

        if self.elapsed_time < par_time:
            # Bonus por terminar rápido
            time_ratio = 1 - (self.elapsed_time / par_time)
            time_bonus = int(base_xp * 0.5 * time_ratio)

        # Penalización por pistas
        hint_penalty = self.hints_used * 10

        # XP final
        final_xp = max(10, base_xp + time_bonus - hint_penalty)

        # Estrellas (1-3)
        stars = 3
        if self.hints_used > 0:
            stars = 2
        if self.hints_used > 2 or self.elapsed_time > par_time * 2:
            stars = 1

        return {
            'score': final_xp * stars,
            'xp': final_xp,
            'stars': stars,
            'details': {
                'base_xp': base_xp,
                'time_bonus': time_bonus,
                'hint_penalty': hint_penalty,
                'time': self.elapsed_time,
                'par_time': par_time,
                'hints_used': self.hints_used,
                'moves': len(self.moves),
            }
        }
