# PromptCraft - Code Editor Component
# Editor de código/prompts interactivo

from browser import document, html, window
from .base import Component
from .button import Button


class CodeEditor(Component):
    """
    Editor de código/prompts con syntax highlighting básico.

    Props:
        value: Contenido inicial
        placeholder: Placeholder text
        language: 'text' | 'prompt' | 'json' | 'python'
        readonly: Solo lectura
        min_height: Altura mínima en px
        max_height: Altura máxima en px
        show_line_numbers: Mostrar números de línea
        on_change: Callback al cambiar contenido
        on_run: Callback al ejecutar (botón Run)
        show_run_button: Mostrar botón de ejecutar
    """

    def __init__(self, **props):
        super().__init__(**props)
        self.textarea = None
        self._value = props.get('value', '')

    def render(self):
        value = self.props.get('value', '')
        placeholder = self.props.get('placeholder', 'Escribe tu prompt aquí...')
        language = self.props.get('language', 'text')
        readonly = self.props.get('readonly', False)
        min_height = self.props.get('min_height', 150)
        max_height = self.props.get('max_height', 400)
        show_line_numbers = self.props.get('show_line_numbers', True)
        on_change = self.props.get('on_change')
        on_run = self.props.get('on_run')
        show_run_button = self.props.get('show_run_button', False)
        label = self.props.get('label', '')

        self._value = value

        container = html.DIV(Class="w-full")

        # Label
        if label:
            container <= html.LABEL(label, Class="block text-sm font-medium text-gray-700 mb-2")

        # Editor container
        editor_container = html.DIV(
            Class="relative border border-gray-200 rounded-lg overflow-hidden bg-gray-900 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500"
        )

        # Header con lenguaje
        header = html.DIV(Class="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700")
        header <= html.SPAN(
            self._get_language_label(language),
            Class="text-xs text-gray-400 font-mono"
        )

        if show_run_button and on_run:
            run_btn = html.BUTTON(
                html.SPAN("▶", Class="mr-1") + "Ejecutar",
                Class="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            )
            run_btn.bind('click', lambda e: on_run(self.get_value()))
            header <= run_btn

        editor_container <= header

        # Editor area
        editor_area = html.DIV(Class="flex")

        # Line numbers
        if show_line_numbers:
            lines = value.split('\n') if value else ['']
            line_nums = html.DIV(
                Class="text-right pr-3 py-3 text-gray-500 text-sm font-mono select-none bg-gray-800 border-r border-gray-700",
                id="line-numbers"
            )
            for i in range(1, len(lines) + 1):
                line_nums <= html.DIV(str(i), Class="leading-6")
            editor_area <= line_nums

        # Textarea
        self.textarea = html.TEXTAREA(
            value,
            Class="flex-1 bg-transparent text-gray-100 font-mono text-sm p-3 resize-none outline-none leading-6",
            placeholder=placeholder,
            readonly=readonly,
            spellcheck=False,
            style=f"min-height: {min_height}px; max-height: {max_height}px;",
            id="code-textarea"
        )

        if on_change:
            self.textarea.bind('input', lambda e: self._handle_change(e, on_change))

        # Auto-resize y actualizar números de línea
        self.textarea.bind('input', self._auto_resize)

        editor_area <= self.textarea
        editor_container <= editor_area

        container <= editor_container

        # Caracteres count
        char_count = html.DIV(
            html.SPAN(f"{len(value)} caracteres", id="char-count"),
            Class="text-xs text-gray-500 mt-1 text-right"
        )
        container <= char_count

        return container

    def _get_language_label(self, language):
        """Obtiene el label del lenguaje."""
        labels = {
            'text': 'Texto',
            'prompt': 'Prompt',
            'json': 'JSON',
            'python': 'Python',
        }
        return labels.get(language, language.upper())

    def _handle_change(self, event, callback):
        """Maneja cambios en el textarea."""
        self._value = event.target.value
        callback(self._value)

        # Actualizar contador de caracteres
        char_count = document.getElementById('char-count')
        if char_count:
            char_count.text = f"{len(self._value)} caracteres"

    def _auto_resize(self, event):
        """Auto-resize del textarea y actualizar números de línea."""
        textarea = event.target
        lines = textarea.value.split('\n')

        # Actualizar números de línea
        line_nums = document.getElementById('line-numbers')
        if line_nums:
            line_nums.innerHTML = ''
            for i in range(1, len(lines) + 1):
                line_nums <= html.DIV(str(i), Class="leading-6")

    def get_value(self):
        """Obtiene el valor actual del editor."""
        if self.textarea:
            return self.textarea.value
        return self._value

    def set_value(self, value):
        """Establece el valor del editor."""
        self._value = value
        if self.textarea:
            self.textarea.value = value


class PromptEditor(CodeEditor):
    """
    Editor especializado para prompts con templates y variables.

    Props adicionales:
        variables: Dict de variables disponibles
        template_mode: Activar modo template {{variable}}
    """

    def render(self):
        self.props['language'] = 'prompt'

        variables = self.props.get('variables', {})
        template_mode = self.props.get('template_mode', False)

        # Render base
        container = super().render()

        # Variables panel si hay variables
        if variables and template_mode:
            vars_panel = self._render_variables_panel(variables)
            container <= vars_panel

        return container

    def _render_variables_panel(self, variables):
        """Renderiza panel de variables disponibles."""
        panel = html.DIV(Class="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200")
        panel <= html.P("Variables disponibles:", Class="text-sm font-medium text-gray-700 mb-2")

        vars_container = html.DIV(Class="flex flex-wrap gap-2")
        for var_name, var_desc in variables.items():
            var_chip = html.BUTTON(
                f"{{{{{var_name}}}}}",
                Class="text-xs px-2 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 cursor-pointer font-mono",
                title=var_desc
            )
            var_chip.bind('click', lambda e, v=var_name: self._insert_variable(v))
            vars_container <= var_chip

        panel <= vars_container
        return panel

    def _insert_variable(self, var_name):
        """Inserta una variable en la posición del cursor."""
        if self.textarea:
            # Obtener posición del cursor
            start = self.textarea.selectionStart
            end = self.textarea.selectionEnd
            value = self.textarea.value

            # Insertar variable
            var_text = f"{{{{{var_name}}}}}"
            new_value = value[:start] + var_text + value[end:]

            self.textarea.value = new_value
            self._value = new_value

            # Mover cursor después de la variable
            new_pos = start + len(var_text)
            self.textarea.setSelectionRange(new_pos, new_pos)
            self.textarea.focus()


def code_editor(**props):
    """Helper para crear editor de código."""
    return CodeEditor(**props).render()


def prompt_editor(**props):
    """Helper para crear editor de prompts."""
    return PromptEditor(**props).render()
