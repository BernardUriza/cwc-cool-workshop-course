# PromptCraft - Button Components
# Botones y controles interactivos

from browser import html
from .base import Component, icon


class Button(Component):
    """
    Componente de botón con variantes.

    Props:
        text: Texto del botón
        variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
        size: 'sm' | 'md' | 'lg'
        icon_name: Nombre del ícono (opcional)
        icon_position: 'left' | 'right'
        disabled: bool
        loading: bool
        full_width: bool
        on_click: Función callback
    """

    VARIANTS = {
        'primary': 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
        'secondary': 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500',
        'outline': 'border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 focus:ring-indigo-500',
        'ghost': 'text-gray-600 hover:bg-gray-100 focus:ring-gray-500',
        'danger': 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
        'success': 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    }

    SIZES = {
        'sm': 'px-3 py-1.5 text-sm',
        'md': 'px-4 py-2 text-base',
        'lg': 'px-6 py-3 text-lg',
    }

    def render(self):
        text = self.props.get('text', '')
        variant = self.props.get('variant', 'primary')
        size = self.props.get('size', 'md')
        icon_name = self.props.get('icon_name')
        icon_position = self.props.get('icon_position', 'left')
        disabled = self.props.get('disabled', False)
        loading = self.props.get('loading', False)
        full_width = self.props.get('full_width', False)
        on_click = self.props.get('on_click')

        # Construir clases
        base_classes = "inline-flex items-center justify-center font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2"
        variant_classes = self.VARIANTS.get(variant, self.VARIANTS['primary'])
        size_classes = self.SIZES.get(size, self.SIZES['md'])
        disabled_classes = "opacity-50 cursor-not-allowed" if disabled or loading else "cursor-pointer"
        width_classes = "w-full" if full_width else ""

        all_classes = f"{base_classes} {variant_classes} {size_classes} {disabled_classes} {width_classes}"

        # Contenido del botón
        content = []

        if loading:
            # Spinner de carga (versión simple)
            content.append(html.SPAN("⏳", Class="animate-spin mr-2"))
            content.append(html.SPAN("Cargando..."))
        else:
            if icon_name and icon_position == 'left':
                content.append(icon(icon_name, size="w-4 h-4 mr-2"))

            if text:
                content.append(html.SPAN(text))

            if icon_name and icon_position == 'right':
                content.append(icon(icon_name, size="w-4 h-4 ml-2"))

        btn = html.BUTTON(
            content,
            Class=all_classes,
            disabled=disabled or loading
        )

        if on_click and not disabled and not loading:
            btn.bind('click', on_click)

        return btn


class IconButton(Component):
    """
    Botón solo con ícono.

    Props:
        icon_name: Nombre del ícono
        variant: 'primary' | 'secondary' | 'ghost'
        size: 'sm' | 'md' | 'lg'
        title: Tooltip
        on_click: Función callback
    """

    SIZES = {
        'sm': 'p-1.5',
        'md': 'p-2',
        'lg': 'p-3',
    }

    ICON_SIZES = {
        'sm': 'w-4 h-4',
        'md': 'w-5 h-5',
        'lg': 'w-6 h-6',
    }

    def render(self):
        icon_name = self.props.get('icon_name', 'x')
        variant = self.props.get('variant', 'ghost')
        size = self.props.get('size', 'md')
        title = self.props.get('title', '')
        on_click = self.props.get('on_click')
        disabled = self.props.get('disabled', False)

        variant_classes = {
            'primary': 'bg-indigo-600 text-white hover:bg-indigo-700',
            'secondary': 'bg-gray-200 text-gray-700 hover:bg-gray-300',
            'ghost': 'text-gray-500 hover:bg-gray-100 hover:text-gray-700',
            'danger': 'text-red-500 hover:bg-red-50 hover:text-red-700',
        }

        base_classes = "inline-flex items-center justify-center rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
        v_classes = variant_classes.get(variant, variant_classes['ghost'])
        s_classes = self.SIZES.get(size, self.SIZES['md'])
        disabled_classes = "opacity-50 cursor-not-allowed" if disabled else ""

        btn = html.BUTTON(
            icon(icon_name, self.ICON_SIZES.get(size, 'w-5 h-5')),
            Class=f"{base_classes} {v_classes} {s_classes} {disabled_classes}",
            title=title,
            disabled=disabled
        )

        if on_click and not disabled:
            btn.bind('click', on_click)

        return btn


def button(text, on_click=None, **props):
    """Función helper para crear botones rápidamente."""
    return Button(text=text, on_click=on_click, **props).render()


def icon_button(icon_name, on_click=None, **props):
    """Función helper para crear botones de ícono."""
    return IconButton(icon_name=icon_name, on_click=on_click, **props).render()
