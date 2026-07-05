# PromptCraft - Base Component
# Clase base para todos los componentes

from browser import document, html


class Component:
    """
    Clase base para componentes UI.
    Proporciona métodos comunes para crear y gestionar elementos DOM.
    """

    def __init__(self, **props):
        self.props = props
        self.element = None
        self._mounted = False

    def render(self):
        """
        Renderiza el componente. Debe ser sobrescrito por subclases.
        Returns: Elemento DOM (html.DIV, etc.)
        """
        raise NotImplementedError("Subclasses must implement render()")

    def mount(self, parent):
        """
        Monta el componente en un elemento padre.

        Args:
            parent: Elemento DOM padre o ID del elemento
        """
        if isinstance(parent, str):
            parent = document.getElementById(parent)

        if not parent:
            raise ValueError("Parent element not found")

        self.element = self.render()
        parent <= self.element
        self._mounted = True
        self.on_mount()
        return self

    def unmount(self):
        """Desmonta el componente del DOM."""
        if self.element and self._mounted:
            self.on_unmount()
            self.element.remove()
            self._mounted = False
        return self

    def update(self, **new_props):
        """
        Actualiza las props y re-renderiza el componente.
        """
        self.props.update(new_props)
        if self._mounted and self.element:
            parent = self.element.parentNode
            old_element = self.element
            self.element = self.render()
            parent.replaceChild(self.element, old_element)
        return self

    def on_mount(self):
        """Callback cuando el componente se monta. Override en subclases."""
        pass

    def on_unmount(self):
        """Callback cuando el componente se desmonta. Override en subclases."""
        pass

    @staticmethod
    def create_icon(path_d, size="w-5 h-5", **attrs):
        """
        Crea un ícono como span (simplificado para compatibilidad).
        """
        # Retorna un span vacío - los iconos se manejan con emojis
        return html.SPAN(Class=size)

    @staticmethod
    def cn(*classes):
        """
        Combina clases CSS, filtrando valores falsy.
        Similar a classnames/clsx en JavaScript.

        Uso:
            cn("base", condition and "conditional", "always")
        """
        return " ".join(filter(None, classes))


# Iconos como emojis (más compatible con Brython)
ICONS = {
    'check': '✓',
    'x': '✕',
    'chevron_right': '›',
    'chevron_left': '‹',
    'chevron_down': '▼',
    'star': '☆',
    'star_filled': '★',
    'lightbulb': '💡',
    'fire': '🔥',
    'trophy': '🏆',
    'lock': '🔒',
    'unlock': '🔓',
    'play': '▶',
    'refresh': '🔄',
    'info': 'ℹ',
    'question': '❓',
    'code': '💻',
    'book': '📖',
    'puzzle': '🧩',
    'home': '🏠',
    'user': '👤',
    'cog': '⚙',
}


def icon(name, size="w-5 h-5", **attrs):
    """
    Crea un ícono por nombre usando emojis.

    Args:
        name: Nombre del ícono (ver ICONS)
        size: Clases de tamaño
        **attrs: Atributos adicionales
    """
    emoji = ICONS.get(name, '❓')
    return html.SPAN(emoji, Class=size)
