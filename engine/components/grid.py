# PromptCraft - Logic Grid Component
# Componente principal para puzzles de eliminación

from browser import document, html
from .base import Component


class LogicGrid(Component):
    """
    Grid de lógica para puzzles de eliminación.

    Props:
        rows: Lista de labels para filas
        cols: Lista de labels para columnas
        grid_state: Dict con estado de celdas {(row, col): 'empty' | 'check' | 'x'}
        row_category: Nombre de la categoría de filas
        col_category: Nombre de la categoría de columnas
        readonly: Si el grid es solo lectura
        on_cell_click: Callback (row_idx, col_idx, new_state)
        show_auto_eliminate: Mostrar eliminación automática
    """

    CELL_STATES = ['empty', 'check', 'x']
    CELL_SYMBOLS = {'empty': '', 'check': '✓', 'x': '✗'}
    CELL_CLASSES = {
        'empty': 'bg-white hover:bg-gray-50',
        'check': 'bg-green-100 text-green-600 font-bold',
        'x': 'bg-red-50 text-red-400',
    }

    def __init__(self, **props):
        super().__init__(**props)
        self.grid_state = props.get('grid_state', {})

    def render(self):
        rows = self.props.get('rows', [])
        cols = self.props.get('cols', [])
        row_category = self.props.get('row_category', 'Filas')
        col_category = self.props.get('col_category', 'Columnas')
        readonly = self.props.get('readonly', False)
        on_cell_click = self.props.get('on_cell_click')

        # Contenedor principal
        container = html.DIV(Class="overflow-x-auto")

        # Tabla del grid
        table = html.TABLE(Class="border-collapse")

        # Header row con categoría de columnas
        header_row = html.TR()
        # Celda vacía esquina
        header_row <= html.TH(
            row_category,
            Class="p-2 text-xs text-gray-500 font-normal text-right border-b border-r border-gray-200"
        )

        for col in cols:
            header_row <= html.TH(
                self._truncate_label(col),
                Class="p-2 text-sm font-medium text-gray-700 border-b border-gray-200 min-w-[60px] text-center",
                title=col
            )

        table <= html.THEAD(header_row)

        # Body con filas
        tbody = html.TBODY()

        for row_idx, row_label in enumerate(rows):
            tr = html.TR()

            # Label de fila
            tr <= html.TH(
                self._truncate_label(row_label),
                Class="p-2 text-sm font-medium text-gray-700 border-r border-gray-200 text-right",
                title=row_label
            )

            # Celdas
            for col_idx, col_label in enumerate(cols):
                cell = self._render_cell(row_idx, col_idx, readonly, on_cell_click)
                tr <= cell

            tbody <= tr

        table <= tbody
        container <= table

        return container

    def _render_cell(self, row_idx, col_idx, readonly, on_cell_click):
        """Renderiza una celda individual del grid."""
        key = (row_idx, col_idx)
        state = self.grid_state.get(key, 'empty')
        symbol = self.CELL_SYMBOLS[state]
        cell_class = self.CELL_CLASSES[state]

        base_classes = "w-12 h-12 text-center border border-gray-200 text-lg transition-colors"
        interactive_class = "cursor-pointer select-none" if not readonly else ""

        cell = html.TD(
            html.SPAN(symbol, Class="block"),
            Class=f"{base_classes} {cell_class} {interactive_class}",
            data_row=str(row_idx),
            data_col=str(col_idx),
            data_state=state
        )

        if not readonly:
            def make_click_handler(r, c):
                def handler(event):
                    self._cycle_cell(r, c, on_cell_click)
                return handler

            cell.bind('click', make_click_handler(row_idx, col_idx))

        return cell

    def _cycle_cell(self, row_idx, col_idx, callback):
        """Cicla el estado de una celda: empty -> check -> x -> empty"""
        key = (row_idx, col_idx)
        current_state = self.grid_state.get(key, 'empty')
        current_idx = self.CELL_STATES.index(current_state)
        new_state = self.CELL_STATES[(current_idx + 1) % 3]

        self.grid_state[key] = new_state

        if callback:
            callback(row_idx, col_idx, new_state)

        # Re-render
        if self._mounted and self.element:
            parent = self.element.parentNode
            self.unmount()
            self.mount(parent)

    def _truncate_label(self, label, max_len=12):
        """Trunca un label si es muy largo."""
        if len(label) > max_len:
            return label[:max_len-1] + '…'
        return label

    def get_state(self):
        """Obtiene el estado actual del grid."""
        return dict(self.grid_state)

    def set_state(self, new_state):
        """Establece el estado del grid."""
        self.grid_state = dict(new_state)
        if self._mounted:
            self.update()

    def clear(self):
        """Limpia el grid."""
        self.grid_state = {}
        if self._mounted:
            self.update()


class MultiGrid(Component):
    """
    Sistema de múltiples grids interconectados para puzzles complejos.

    Props:
        categories: Lista de categorías [{name, items}]
        grid_states: Dict de estados por par de categorías
        on_cell_change: Callback global
    """

    def __init__(self, **props):
        super().__init__(**props)
        self.grids = {}
        self.grid_states = props.get('grid_states', {})

    def render(self):
        categories = self.props.get('categories', [])
        on_cell_change = self.props.get('on_cell_change')

        container = html.DIV(Class="space-y-6")

        # Crear grids para cada par de categorías (triángulo superior)
        for i in range(len(categories)):
            for j in range(i + 1, len(categories)):
                cat1 = categories[i]
                cat2 = categories[j]

                grid_key = f"{cat1['name']}__{cat2['name']}"
                grid_state = self.grid_states.get(grid_key, {})

                # Wrapper
                grid_wrapper = html.DIV(Class="bg-white rounded-lg p-4 shadow-sm border border-gray-100")

                # Título
                grid_wrapper <= html.H4(
                    f"{cat1['name']} vs {cat2['name']}",
                    Class="text-sm font-medium text-gray-600 mb-3"
                )

                # Grid
                grid = LogicGrid(
                    rows=cat1['items'],
                    cols=cat2['items'],
                    row_category=cat1['name'],
                    col_category=cat2['name'],
                    grid_state=grid_state,
                    on_cell_click=lambda r, c, s, k=grid_key: self._handle_cell_change(k, r, c, s, on_cell_change)
                )

                self.grids[grid_key] = grid
                grid_wrapper <= grid.render()
                container <= grid_wrapper

        return container

    def _handle_cell_change(self, grid_key, row_idx, col_idx, new_state, callback):
        """Maneja cambios en cualquier celda de cualquier grid."""
        if grid_key not in self.grid_states:
            self.grid_states[grid_key] = {}

        self.grid_states[grid_key][(row_idx, col_idx)] = new_state

        # Auto-eliminación si es un check
        if new_state == 'check':
            self._auto_eliminate(grid_key, row_idx, col_idx)

        if callback:
            callback(grid_key, row_idx, col_idx, new_state)

    def _auto_eliminate(self, grid_key, row_idx, col_idx):
        """
        Cuando se marca un ✓, automáticamente marca ✗ en:
        - Resto de la fila
        - Resto de la columna
        """
        categories = self.props.get('categories', [])

        # Encontrar categorías de este grid
        cat_names = grid_key.split('__')
        cat1 = next((c for c in categories if c['name'] == cat_names[0]), None)
        cat2 = next((c for c in categories if c['name'] == cat_names[1]), None)

        if not cat1 or not cat2:
            return

        grid_state = self.grid_states.get(grid_key, {})

        # Marcar X en el resto de la fila
        for c in range(len(cat2['items'])):
            if c != col_idx:
                key = (row_idx, c)
                if grid_state.get(key, 'empty') == 'empty':
                    grid_state[key] = 'x'

        # Marcar X en el resto de la columna
        for r in range(len(cat1['items'])):
            if r != row_idx:
                key = (r, col_idx)
                if grid_state.get(key, 'empty') == 'empty':
                    grid_state[key] = 'x'

        self.grid_states[grid_key] = grid_state

    def get_all_states(self):
        """Obtiene todos los estados de todos los grids."""
        return dict(self.grid_states)

    def verify_solution(self, solution):
        """
        Verifica si la solución actual es correcta.

        Args:
            solution: Dict con la solución correcta por grid
        """
        for grid_key, expected in solution.items():
            actual = self.grid_states.get(grid_key, {})

            # Solo verificar checks
            for key, value in expected.items():
                if value == 'check':
                    if actual.get(key) != 'check':
                        return False

        return True


def logic_grid(**props):
    """Helper para crear grid de lógica."""
    return LogicGrid(**props).render()


def multi_grid(**props):
    """Helper para crear sistema multi-grid."""
    return MultiGrid(**props)
