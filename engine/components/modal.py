# PromptCraft - Modal Component
# Ventanas modales y diálogos

from browser import document, html, window
from .base import Component, icon
from .button import Button


class Modal(Component):
    """
    Componente de modal/diálogo.

    Props:
        title: Título del modal
        content: Contenido (string o elemento DOM)
        footer: Contenido del footer (botones, etc.)
        size: 'sm' | 'md' | 'lg' | 'xl' | 'full'
        closable: Mostrar botón de cerrar
        close_on_overlay: Cerrar al hacer clic en overlay
        on_close: Callback al cerrar
    """

    SIZES = {
        'sm': 'max-w-sm',
        'md': 'max-w-md',
        'lg': 'max-w-lg',
        'xl': 'max-w-xl',
        'full': 'max-w-4xl',
    }

    def __init__(self, **props):
        super().__init__(**props)
        self.overlay = None
        self._bound_key_handler = None

    def render(self):
        title = self.props.get('title', '')
        content = self.props.get('content', '')
        footer = self.props.get('footer')
        size = self.props.get('size', 'md')
        closable = self.props.get('closable', True)
        close_on_overlay = self.props.get('close_on_overlay', True)
        on_close = self.props.get('on_close')

        size_class = self.SIZES.get(size, self.SIZES['md'])

        # Overlay
        overlay = html.DIV(
            Class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fade-in"
        )
        self.overlay = overlay

        if close_on_overlay:
            overlay.bind('click', lambda e: self._handle_overlay_click(e, on_close))

        # Modal container
        modal = html.DIV(
            Class=f"bg-white rounded-xl shadow-xl w-full {size_class} max-h-[90vh] flex flex-col animate-scale-in"
        )
        modal.bind('click', lambda e: e.stopPropagation())

        # Header
        if title or closable:
            header = html.DIV(Class="flex items-center justify-between p-4 border-b border-gray-100")

            if title:
                header <= html.H2(title, Class="text-lg font-semibold text-gray-800")
            else:
                header <= html.DIV()  # Spacer

            if closable:
                close_btn = html.BUTTON(
                    icon('x', 'w-5 h-5'),
                    Class="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                )
                close_btn.bind('click', lambda e: self._close(on_close))
                header <= close_btn

            modal <= header

        # Content
        content_div = html.DIV(Class="p-4 overflow-y-auto flex-1")
        if isinstance(content, str):
            content_div <= html.P(content, Class="text-gray-600")
        else:
            content_div <= content
        modal <= content_div

        # Footer
        if footer:
            footer_div = html.DIV(Class="p-4 border-t border-gray-100 flex justify-end gap-2")
            if isinstance(footer, str):
                footer_div <= html.P(footer)
            else:
                footer_div <= footer
            modal <= footer_div

        overlay <= modal
        return overlay

    def _handle_overlay_click(self, event, on_close):
        """Maneja clic en el overlay."""
        if event.target == self.overlay:
            self._close(on_close)

    def _close(self, on_close=None):
        """Cierra el modal."""
        if on_close:
            on_close()
        self.unmount()

    def on_mount(self):
        """Al montar, añadir listener de tecla Escape."""
        def key_handler(event):
            if event.key == 'Escape':
                on_close = self.props.get('on_close')
                self._close(on_close)

        self._bound_key_handler = key_handler
        document.bind('keydown', key_handler)

        # Prevenir scroll del body
        document.body.style.overflow = 'hidden'

    def on_unmount(self):
        """Al desmontar, limpiar listeners."""
        if self._bound_key_handler:
            document.unbind('keydown', self._bound_key_handler)

        # Restaurar scroll
        document.body.style.overflow = ''

    def show(self):
        """Muestra el modal montándolo en el body."""
        self.mount(document.body)
        return self

    def hide(self):
        """Oculta el modal."""
        self.unmount()
        return self


class ConfirmModal(Modal):
    """
    Modal de confirmación con botones Aceptar/Cancelar.

    Props:
        title: Título
        message: Mensaje de confirmación
        confirm_text: Texto del botón confirmar
        cancel_text: Texto del botón cancelar
        confirm_variant: Variante del botón confirmar
        on_confirm: Callback al confirmar
        on_cancel: Callback al cancelar
    """

    def render(self):
        message = self.props.get('message', '¿Estás seguro?')
        confirm_text = self.props.get('confirm_text', 'Confirmar')
        cancel_text = self.props.get('cancel_text', 'Cancelar')
        confirm_variant = self.props.get('confirm_variant', 'primary')
        on_confirm = self.props.get('on_confirm')
        on_cancel = self.props.get('on_cancel')

        # Crear footer con botones
        footer = html.DIV(Class="flex gap-2")

        cancel_btn = Button(
            text=cancel_text,
            variant='ghost',
            on_click=lambda e: self._handle_cancel(on_cancel)
        ).render()

        confirm_btn = Button(
            text=confirm_text,
            variant=confirm_variant,
            on_click=lambda e: self._handle_confirm(on_confirm)
        ).render()

        footer <= cancel_btn
        footer <= confirm_btn

        # Actualizar props con footer
        self.props['content'] = html.P(message, Class="text-gray-600")
        self.props['footer'] = footer
        self.props['size'] = 'sm'

        return super().render()

    def _handle_confirm(self, on_confirm):
        if on_confirm:
            on_confirm()
        self.unmount()

    def _handle_cancel(self, on_cancel):
        if on_cancel:
            on_cancel()
        self.unmount()


class SuccessModal(Modal):
    """
    Modal de éxito/celebración.

    Props:
        title: Título
        message: Mensaje
        xp_gained: XP ganado
        badge_earned: Badge desbloqueado (opcional)
        on_close: Callback al cerrar
    """

    def render(self):
        message = self.props.get('message', '¡Lo lograste!')
        xp_gained = self.props.get('xp_gained', 0)
        badge_earned = self.props.get('badge_earned')
        on_close = self.props.get('on_close')

        # Contenido
        content = html.DIV(Class="text-center py-4")

        # Emoji de celebración
        content <= html.SPAN("🎉", Class="text-6xl block mb-4")

        # Mensaje
        content <= html.P(message, Class="text-lg text-gray-700 mb-4")

        # XP ganado
        if xp_gained > 0:
            content <= html.DIV(
                html.SPAN(f"+{xp_gained}", Class="text-2xl font-bold text-indigo-600") +
                html.SPAN(" XP", Class="text-lg text-gray-500"),
                Class="mb-4"
            )

        # Badge ganado
        if badge_earned:
            badge_div = html.DIV(Class="bg-yellow-50 rounded-lg p-4 mb-4")
            badge_div <= html.P("🏆 ¡Nuevo badge desbloqueado!", Class="text-sm text-yellow-700 mb-2")
            badge_div <= html.P(badge_earned.get('name', ''), Class="font-bold text-yellow-800")
            content <= badge_div

        # Footer con botón
        footer = html.DIV(
            Button(
                text="¡Genial!",
                variant='primary',
                full_width=True,
                on_click=lambda e: self._close(on_close)
            ).render()
        )

        self.props['content'] = content
        self.props['footer'] = footer
        self.props['size'] = 'sm'
        self.props['title'] = self.props.get('title', '¡Felicitaciones!')

        return super().render()


def modal(**props):
    """Helper para crear modales."""
    return Modal(**props)


def confirm(message, on_confirm=None, **props):
    """Helper para crear modal de confirmación."""
    return ConfirmModal(message=message, on_confirm=on_confirm, **props).show()


def success(message, **props):
    """Helper para crear modal de éxito."""
    return SuccessModal(message=message, **props).show()
