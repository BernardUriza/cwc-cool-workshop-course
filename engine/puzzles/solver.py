# PromptCraft - Puzzle Solver
# Algoritmos para resolver y validar puzzles

class PuzzleSolver:
    """
    Solver de puzzles de lógica.
    Puede resolver puzzles automáticamente o dar pistas.
    """

    def __init__(self, puzzle_data):
        self.puzzle_data = puzzle_data
        self.categories = puzzle_data.get('categories', [])
        self.clues = puzzle_data.get('clues', [])
        self.solution = puzzle_data.get('solution', {})

        # Estado de trabajo
        self.grid_states = {}
        self._init_grids()

    def _init_grids(self):
        """Inicializa grids vacíos."""
        for i in range(len(self.categories)):
            for j in range(i + 1, len(self.categories)):
                cat1 = self.categories[i]
                cat2 = self.categories[j]
                grid_key = f"{cat1['name']}__{cat2['name']}"
                self.grid_states[grid_key] = {}

    def solve(self, max_iterations=100):
        """
        Intenta resolver el puzzle completamente.

        Returns:
            Dict con el estado resuelto o None si no se pudo resolver
        """
        for _ in range(max_iterations):
            changed = False

            # Aplicar cada pista
            for clue in self.clues:
                if self._apply_clue(clue):
                    changed = True

            # Aplicar lógica de eliminación
            if self._apply_elimination_logic():
                changed = True

            # Verificar si está completo
            if self._is_complete():
                return self.grid_states

            # Si no hubo cambios, no podemos avanzar más
            if not changed:
                break

        return None

    def _apply_clue(self, clue):
        """
        Intenta aplicar una pista al estado actual.

        Args:
            clue: Dict con la definición de la pista

        Returns:
            True si se hizo algún cambio
        """
        clue_type = clue.get('type', 'direct')

        if clue_type == 'direct':
            # Pista directa: "X es Y"
            return self._apply_direct_clue(clue)
        elif clue_type == 'not':
            # Pista negativa: "X no es Y"
            return self._apply_not_clue(clue)
        elif clue_type == 'either_or':
            # Pista de opciones: "X es Y o Z"
            return self._apply_either_or_clue(clue)
        elif clue_type == 'if_then':
            # Pista condicional: "Si X es Y, entonces Z es W"
            return self._apply_if_then_clue(clue)

        return False

    def _apply_direct_clue(self, clue):
        """Aplica una pista directa."""
        subject = clue.get('subject')  # (category, item)
        obj = clue.get('object')  # (category, item)

        if not subject or not obj:
            return False

        grid_key = self._get_grid_key(subject[0], obj[0])
        if not grid_key:
            return False

        row = self._get_item_index(subject[0], subject[1])
        col = self._get_item_index(obj[0], obj[1])

        if row is None or col is None:
            return False

        # Ajustar orden si es necesario
        if not grid_key.startswith(subject[0]):
            row, col = col, row

        current = self.grid_states[grid_key].get((row, col), 'empty')
        if current == 'empty':
            self.grid_states[grid_key][(row, col)] = 'check'
            self._auto_eliminate(grid_key, row, col)
            return True

        return False

    def _apply_not_clue(self, clue):
        """Aplica una pista negativa."""
        subject = clue.get('subject')
        obj = clue.get('object')

        if not subject or not obj:
            return False

        grid_key = self._get_grid_key(subject[0], obj[0])
        if not grid_key:
            return False

        row = self._get_item_index(subject[0], subject[1])
        col = self._get_item_index(obj[0], obj[1])

        if row is None or col is None:
            return False

        if not grid_key.startswith(subject[0]):
            row, col = col, row

        current = self.grid_states[grid_key].get((row, col), 'empty')
        if current == 'empty':
            self.grid_states[grid_key][(row, col)] = 'x'
            return True

        return False

    def _apply_either_or_clue(self, clue):
        """Aplica una pista de opciones."""
        # Si una opción está eliminada, la otra debe ser correcta
        subject = clue.get('subject')
        options = clue.get('options', [])

        if not subject or len(options) < 2:
            return False

        eliminated = []
        possible = []

        for opt in options:
            grid_key = self._get_grid_key(subject[0], opt[0])
            if not grid_key:
                continue

            row = self._get_item_index(subject[0], subject[1])
            col = self._get_item_index(opt[0], opt[1])

            if row is None or col is None:
                continue

            if not grid_key.startswith(subject[0]):
                row, col = col, row

            state = self.grid_states[grid_key].get((row, col), 'empty')

            if state == 'x':
                eliminated.append(opt)
            elif state == 'empty':
                possible.append((grid_key, row, col, opt))

        # Si solo queda una opción posible, marcarla
        if len(possible) == 1 and len(eliminated) == len(options) - 1:
            grid_key, row, col, opt = possible[0]
            self.grid_states[grid_key][(row, col)] = 'check'
            self._auto_eliminate(grid_key, row, col)
            return True

        return False

    def _apply_if_then_clue(self, clue):
        """Aplica una pista condicional."""
        # Si la condición es verdadera, aplicar la consecuencia
        condition = clue.get('condition')  # (cat1, item1, cat2, item2)
        consequence = clue.get('consequence')  # (cat3, item3, cat4, item4)

        if not condition or not consequence:
            return False

        # Verificar si la condición es verdadera
        grid_key = self._get_grid_key(condition[0], condition[2])
        if not grid_key:
            return False

        row = self._get_item_index(condition[0], condition[1])
        col = self._get_item_index(condition[2], condition[3])

        if row is None or col is None:
            return False

        if not grid_key.startswith(condition[0]):
            row, col = col, row

        if self.grid_states[grid_key].get((row, col)) == 'check':
            # Condición verdadera, aplicar consecuencia
            return self._apply_direct_clue({
                'subject': (consequence[0], consequence[1]),
                'object': (consequence[2], consequence[3])
            })

        return False

    def _apply_elimination_logic(self):
        """
        Aplica lógica de eliminación automática.
        - Si una fila/columna tiene n-1 X's, la celda restante es ✓
        - Si hay un ✓ en una celda, las demás en esa fila/columna son X
        """
        changed = False

        for grid_key, grid in self.grid_states.items():
            cat_names = grid_key.split('__')
            cat1 = next((c for c in self.categories if c['name'] == cat_names[0]), None)
            cat2 = next((c for c in self.categories if c['name'] == cat_names[1]), None)

            if not cat1 or not cat2:
                continue

            rows = len(cat1['items'])
            cols = len(cat2['items'])

            # Verificar cada fila
            for r in range(rows):
                empty_cells = []
                has_check = False

                for c in range(cols):
                    state = grid.get((r, c), 'empty')
                    if state == 'empty':
                        empty_cells.append(c)
                    elif state == 'check':
                        has_check = True

                # Si hay exactamente una celda vacía y no hay check
                if len(empty_cells) == 1 and not has_check:
                    grid[(r, empty_cells[0])] = 'check'
                    self._auto_eliminate(grid_key, r, empty_cells[0])
                    changed = True

            # Verificar cada columna
            for c in range(cols):
                empty_cells = []
                has_check = False

                for r in range(rows):
                    state = grid.get((r, c), 'empty')
                    if state == 'empty':
                        empty_cells.append(r)
                    elif state == 'check':
                        has_check = True

                if len(empty_cells) == 1 and not has_check:
                    grid[(empty_cells[0], c)] = 'check'
                    self._auto_eliminate(grid_key, empty_cells[0], c)
                    changed = True

        return changed

    def _auto_eliminate(self, grid_key, row, col):
        """Auto-elimina cuando se marca un check."""
        cat_names = grid_key.split('__')
        cat1 = next((c for c in self.categories if c['name'] == cat_names[0]), None)
        cat2 = next((c for c in self.categories if c['name'] == cat_names[1]), None)

        if not cat1 or not cat2:
            return

        grid = self.grid_states[grid_key]

        # X en resto de fila
        for c in range(len(cat2['items'])):
            if c != col and grid.get((row, c), 'empty') == 'empty':
                grid[(row, c)] = 'x'

        # X en resto de columna
        for r in range(len(cat1['items'])):
            if r != row and grid.get((r, col), 'empty') == 'empty':
                grid[(r, col)] = 'x'

    def _get_grid_key(self, cat1_name, cat2_name):
        """Obtiene la clave del grid para dos categorías."""
        for key in self.grid_states:
            parts = key.split('__')
            if (cat1_name in parts) and (cat2_name in parts):
                return key
        return None

    def _get_item_index(self, category_name, item_name):
        """Obtiene el índice de un item en una categoría."""
        for cat in self.categories:
            if cat['name'] == category_name:
                try:
                    return cat['items'].index(item_name)
                except ValueError:
                    return None
        return None

    def _is_complete(self):
        """Verifica si el puzzle está completo."""
        for grid_key, grid in self.grid_states.items():
            cat_names = grid_key.split('__')
            cat1 = next((c for c in self.categories if c['name'] == cat_names[0]), None)

            if not cat1:
                continue

            # Cada fila debe tener exactamente un check
            for r in range(len(cat1['items'])):
                has_check = False
                for c in range(len(cat1['items'])):
                    if grid.get((r, c)) == 'check':
                        has_check = True
                        break
                if not has_check:
                    return False

        return True

    def get_hint(self, current_state):
        """
        Genera una pista basada en el estado actual.

        Args:
            current_state: Estado actual del puzzle

        Returns:
            Dict con la pista o None
        """
        # Copiar estado actual
        self.grid_states = {k: dict(v) for k, v in current_state.items()}

        # Intentar un paso de solución
        for clue in self.clues:
            if self._apply_clue(clue):
                # Encontrar qué cambió
                for grid_key, grid in self.grid_states.items():
                    for key, value in grid.items():
                        original = current_state.get(grid_key, {}).get(key, 'empty')
                        if original != value:
                            return {
                                'grid': grid_key,
                                'cell': key,
                                'action': value,
                                'clue': clue.get('text', '')
                            }

        return None


def validate_solution(puzzle_data, grid_states):
    """
    Valida si una solución es correcta.

    Args:
        puzzle_data: Datos del puzzle
        grid_states: Estado de los grids a validar

    Returns:
        True si la solución es correcta
    """
    solution = puzzle_data.get('solution', {})

    for grid_key, expected_grid in solution.items():
        actual_grid = grid_states.get(grid_key, {})

        for key_str, expected_state in expected_grid.items():
            if expected_state == 'check':
                # Parsear key si es string
                if isinstance(key_str, str):
                    row, col = map(int, key_str.split(','))
                    key = (row, col)
                else:
                    key = key_str

                if actual_grid.get(key) != 'check':
                    return False

    return True
