# PromptCraft - Toast Notifications
# Sistema de notificaciones toast

from browser import document, html, timer
from .base import Component, icon


class Toast(Component):
    """
    Notificación toast.

    Props:
        message: Mensaje a mostrar
        type: 'success' | 'error' | 'warning' | 'info'
        duration: Duración en ms (0 = sin auto-dismiss)
        position: 'top-right' | 'top-center' | 'bottom-right' | 'bottom-center'
        dismissible: Mostrar botón de cerrar
        on_dismiss: Callback al cerrar
    """

    TYPES = {
        'success': {
            'icon': 'check',
            'bg': 'bg-green-50',
            'border': 'border-green-200',
            'text': 'text-green-800',
            'icon_color': 'text-green-500',
        },
        'error': {
            'icon': 'x',
            'bg': 'bg-red-50',
            'border': 'border-red-200',
            'text': 'text-red-800',
            'icon_color': 'text-red-500',
        },
        'warning': {
            'icon': 'info',
            'bg': 'bg-yellow-50',
            'border': 'border-yellow-200',
            'text': 'text-yellow-800',
            'icon_color': 'text-yellow-500',
        },
        'info': {
            'icon': 'info',
            'bg': 'bg-blue-50',
            'border': 'border-blue-200',
            'text': 'text-blue-800',
            'icon_color': 'text-blue-500',
        },
    }

    POSITIONS = {
        'top-right': 'top-4 right-4',
        'top-center': 'top-4 left-1/2 -translate-x-1/2',
        'bottom-right': 'bottom-4 right-4',
        'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
    }

    def __init__(self, **props):
        super().__init__(**props)
        self._timer_id = None

    def render(self):
        message = self.props.get('message', '')
        toast_type = self.props.get('type', 'info')
        dismissible = self.props.get('dismissible', True)
        on_dismiss = self.props.get('on_dismiss')

        type_config = self.TYPES.get(toast_type, self.TYPES['info'])

        toast = html.DIV(
            Class=f"flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg {type_config['bg']} {type_config['border']} animate-slide-in"
        )

        # Icono
        toast <= html.DIV(
            icon(type_config['icon'], 'w-5 h-5'),
            Class=type_config['icon_color']
        )

        # Mensaje
        toast <= html.P(
            message,
            Class=f"flex-1 text-sm font-medium {type_config['text']}"
        )

        # Botón cerrar
        if dismissible:
            close_btn = html.BUTTON(
                icon('x', 'w-4 h-4'),
                Class=f"p-1 rounded hover:bg-black/10 transition-colors {type_config['text']}"
            )
            close_btn.bind('click', lambda e: self._dismiss(on_dismiss))
            toast <= close_btn

        return toast

    def show(self, container_id='toast-container'):
        """Muestra el toast."""
        # Asegurar que existe el contenedor
        container = document.getElementById(container_id)
        if not container:
            position = self.props.get('position', 'top-right')
            pos_classes = self.POSITIONS.get(position, self.POSITIONS['top-right'])

            container = html.DIV(
                Class=f"fixed {pos_classes} z-50 space-y-2",
                id=container_id
            )
            document.body <= container

        self.mount(container)

        # Auto-dismiss
        duration = self.props.get('duration', 3000)
        if duration > 0:
            self._timer_id = timer.set_timeout(
                lambda: self._dismiss(self.props.get('on_dismiss')),
                duration
            )

        return self

    def _dismiss(self, callback=None):
        """Cierra el toast."""
        if self._timer_id:
            timer.clear_timeout(self._timer_id)

        if callback:
            callback()

        self.unmount()

    def on_unmount(self):
        """Limpia timer al desmontar."""
        if self._timer_id:
            timer.clear_timeout(self._timer_id)


# Sistema global de toasts
_toast_queue = []

def show_toast(message, type='info', **props):
    """
    Muestra un toast de forma rápida.

    Args:
        message: Mensaje a mostrar
        type: 'success' | 'error' | 'warning' | 'info'
        **props: Props adicionales
    """
    toast = Toast(message=message, type=type, **props)
    toast.show()
    return toast


def success(message, **props):
    """Muestra toast de éxito."""
    return show_toast(message, type='success', **props)


def error(message, **props):
    """Muestra toast de error."""
    return show_toast(message, type='error', **props)


def warning(message, **props):
    """Muestra toast de advertencia."""
    return show_toast(message, type='warning', **props)


def info(message, **props):
    """Muestra toast informativo."""
    return show_toast(message, type='info', **props)


def xp_toast(xp_amount, reason=''):
    """
    Toast especial para ganar XP.

    Args:
        xp_amount: Cantidad de XP ganado
        reason: Razón del XP
    """
    message = f"+{xp_amount} XP"
    if reason:
        message += f" - {reason}"

    toast = html.DIV(
        Class="flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg bg-indigo-600 border-indigo-700 animate-bounce-in"
    )

    toast <= html.SPAN("⭐", Class="text-xl")
    toast <= html.P(message, Class="text-sm font-bold text-white")

    # Mostrar directamente
    container = document.getElementById('toast-container')
    if not container:
        container = html.DIV(
            Class="fixed top-4 right-4 z-50 space-y-2",
            id="toast-container"
        )
        document.body <= container

    container <= toast

    # Auto remove
    def remove():
        try:
            toast.remove()
        except:
            pass

    timer.set_timeout(remove, 2500)


def badge_toast(badge_name, badge_icon='🏆'):
    """
    Toast especial para nuevo badge.

    Args:
        badge_name: Nombre del badge
        badge_icon: Emoji del badge
    """
    toast = html.DIV(
        Class="flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg bg-gradient-to-r from-yellow-400 to-amber-500 border-yellow-600 animate-bounce-in"
    )

    toast <= html.SPAN(badge_icon, Class="text-2xl")
    toast <= html.DIV(
        html.P("¡Nuevo Badge!", Class="text-xs text-yellow-900") +
        html.P(badge_name, Class="text-sm font-bold text-white"),
    )

    container = document.getElementById('toast-container')
    if not container:
        container = html.DIV(
            Class="fixed top-4 right-4 z-50 space-y-2",
            id="toast-container"
        )
        document.body <= container

    container <= toast

    def remove():
        try:
            toast.remove()
        except:
            pass

    timer.set_timeout(remove, 4000)
