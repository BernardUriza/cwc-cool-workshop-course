# PromptCraft - Puzzle Timer
# Componente de cronómetro para puzzles

from browser import document, html, timer as browser_timer
from ..components.base import Component


class PuzzleTimer(Component):
    """
    Cronómetro para puzzles.

    Props:
        initial_time: Tiempo inicial en segundos
        count_down: Si es cuenta regresiva
        on_timeout: Callback si llega a 0 (solo countdown)
        show_milliseconds: Mostrar milisegundos
    """

    def __init__(self, **props):
        super().__init__(**props)
        self.elapsed = props.get('initial_time', 0)
        self.is_running = False
        self._interval_id = None
        self._display_elem = None

    def render(self):
        count_down = self.props.get('count_down', False)
        show_milliseconds = self.props.get('show_milliseconds', False)

        container = html.DIV(Class="flex items-center gap-2 bg-gray-100 rounded-lg px-3 py-2")

        # Icono de reloj
        container <= html.SPAN("⏱️", Class="text-lg")

        # Display del tiempo
        self._display_elem = html.SPAN(
            self._format_time(),
            Class="font-mono text-lg font-medium text-gray-700",
            id="timer-display"
        )
        container <= self._display_elem

        return container

    def _format_time(self):
        """Formatea el tiempo para mostrar."""
        count_down = self.props.get('count_down', False)
        show_milliseconds = self.props.get('show_milliseconds', False)

        if count_down:
            initial = self.props.get('initial_time', 0)
            remaining = max(0, initial - self.elapsed)
            time_val = remaining
        else:
            time_val = self.elapsed

        minutes = time_val // 60
        seconds = time_val % 60

        if show_milliseconds:
            ms = int((self.elapsed * 1000) % 1000 / 10)
            return f"{minutes:02d}:{seconds:02d}.{ms:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def _update_display(self):
        """Actualiza el display del timer."""
        if self._display_elem:
            self._display_elem.text = self._format_time()

    def _tick(self):
        """Tick del timer (cada segundo)."""
        self.elapsed += 1
        self._update_display()

        # Verificar timeout en countdown
        count_down = self.props.get('count_down', False)
        if count_down:
            initial = self.props.get('initial_time', 0)
            if self.elapsed >= initial:
                self.stop()
                on_timeout = self.props.get('on_timeout')
                if on_timeout:
                    on_timeout()

    def start(self):
        """Inicia el cronómetro."""
        if self.is_running:
            return

        self.is_running = True
        self._interval_id = browser_timer.set_interval(self._tick, 1000)

    def stop(self):
        """Detiene el cronómetro."""
        if not self.is_running:
            return

        self.is_running = False
        if self._interval_id:
            browser_timer.clear_interval(self._interval_id)
            self._interval_id = None

    def reset(self):
        """Reinicia el cronómetro."""
        self.stop()
        self.elapsed = self.props.get('initial_time', 0) if self.props.get('count_down') else 0
        self._update_display()

    def get_elapsed(self):
        """Obtiene el tiempo transcurrido."""
        return self.elapsed

    def get_remaining(self):
        """Obtiene el tiempo restante (solo countdown)."""
        initial = self.props.get('initial_time', 0)
        return max(0, initial - self.elapsed)

    def add_time(self, seconds):
        """Añade tiempo (útil para bonificaciones)."""
        if self.props.get('count_down'):
            self.elapsed = max(0, self.elapsed - seconds)
        else:
            self.elapsed += seconds
        self._update_display()

    def on_unmount(self):
        """Limpia el timer al desmontar."""
        self.stop()


class CountdownTimer(PuzzleTimer):
    """Timer de cuenta regresiva."""

    def __init__(self, **props):
        props['count_down'] = True
        super().__init__(**props)

    def render(self):
        container = html.DIV(Class="flex items-center gap-2 bg-red-50 rounded-lg px-3 py-2 border border-red-100")

        # Icono de reloj
        container <= html.SPAN("⏳", Class="text-lg")

        # Display del tiempo
        self._display_elem = html.SPAN(
            self._format_time(),
            Class="font-mono text-lg font-medium text-red-700",
            id="countdown-display"
        )
        container <= self._display_elem

        return container


def puzzle_timer(**props):
    """Helper para crear timer de puzzle."""
    return PuzzleTimer(**props)


def countdown_timer(seconds, on_timeout=None, **props):
    """Helper para crear timer de cuenta regresiva."""
    return CountdownTimer(initial_time=seconds, on_timeout=on_timeout, **props)
