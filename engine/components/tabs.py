# PromptCraft - Tabs Component
# Sistema de pestañas

from browser import html
from .base import Component


class Tabs(Component):
    """
    Componente de pestañas.

    Props:
        tabs: Lista de dicts con {id, label, icon?, content}
        active_tab: ID de la pestaña activa
        on_change: Callback al cambiar de pestaña
        variant: 'underline' | 'pills' | 'boxed'
    """

    def __init__(self, **props):
        super().__init__(**props)
        self.active_tab = props.get('active_tab') or (props.get('tabs', [{}])[0].get('id') if props.get('tabs') else None)

    def render(self):
        tabs = self.props.get('tabs', [])
        variant = self.props.get('variant', 'underline')
        on_change = self.props.get('on_change')

        container = html.DIV(Class="w-full")

        # Tab headers
        headers = self._render_headers(tabs, variant, on_change)
        container <= headers

        # Tab content
        content = self._render_content(tabs)
        container <= content

        return container

    def _render_headers(self, tabs, variant, on_change):
        """Renderiza los headers de las pestañas."""
        variant_styles = {
            'underline': {
                'container': 'flex border-b border-gray-200',
                'tab': 'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                'active': 'border-indigo-500 text-indigo-600',
                'inactive': 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            },
            'pills': {
                'container': 'flex gap-2 p-1 bg-gray-100 rounded-lg',
                'tab': 'px-4 py-2 text-sm font-medium rounded-md transition-colors',
                'active': 'bg-white text-gray-900 shadow-sm',
                'inactive': 'text-gray-500 hover:text-gray-700',
            },
            'boxed': {
                'container': 'flex',
                'tab': 'px-4 py-2 text-sm font-medium border border-gray-200 first:rounded-l-lg last:rounded-r-lg -ml-px first:ml-0 transition-colors',
                'active': 'bg-indigo-50 border-indigo-200 text-indigo-700 z-10',
                'inactive': 'bg-white text-gray-500 hover:bg-gray-50',
            },
        }

        styles = variant_styles.get(variant, variant_styles['underline'])
        headers = html.DIV(Class=styles['container'])

        for tab in tabs:
            tab_id = tab.get('id', '')
            label = tab.get('label', '')
            icon_emoji = tab.get('icon', '')
            is_active = tab_id == self.active_tab

            tab_class = f"{styles['tab']} {styles['active'] if is_active else styles['inactive']} cursor-pointer"

            tab_content = []
            if icon_emoji:
                tab_content.append(html.SPAN(icon_emoji, Class="mr-2"))
            tab_content.append(html.SPAN(label))

            tab_btn = html.BUTTON(
                tab_content,
                Class=tab_class,
                data_tab=tab_id
            )

            def make_handler(tid):
                def handler(e):
                    self._switch_tab(tid, on_change)
                return handler

            tab_btn.bind('click', make_handler(tab_id))
            headers <= tab_btn

        return headers

    def _render_content(self, tabs):
        """Renderiza el contenido de la pestaña activa."""
        content_container = html.DIV(Class="mt-4", id="tab-content")

        for tab in tabs:
            if tab.get('id') == self.active_tab:
                content = tab.get('content', '')
                if isinstance(content, str):
                    content_container <= html.P(content)
                elif callable(content):
                    content_container <= content()
                else:
                    content_container <= content
                break

        return content_container

    def _switch_tab(self, tab_id, on_change):
        """Cambia a otra pestaña."""
        if tab_id != self.active_tab:
            self.active_tab = tab_id
            if on_change:
                on_change(tab_id)
            # Re-render
            if self.element:
                parent = self.element.parentNode
                self.unmount()
                self.mount(parent)


class TabPanel(Component):
    """
    Panel individual de contenido de tab.

    Props:
        content: Contenido del panel
        padding: Aplicar padding
    """

    def render(self):
        content = self.props.get('content', '')
        padding = self.props.get('padding', True)

        panel = html.DIV(Class="p-4" if padding else "")

        if isinstance(content, str):
            panel <= html.P(content, Class="text-gray-600")
        elif callable(content):
            panel <= content()
        else:
            panel <= content

        return panel


def tabs(tabs_config, **props):
    """Helper para crear tabs."""
    return Tabs(tabs=tabs_config, **props).render()
