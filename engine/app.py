# CWC - Main Application Module

from browser import document, html, window

from .state import get_state
from .router import get_router, navigate
from .config import get_config, feature_enabled


class App:
    """
    Aplicación principal de PromptCraft.
    Coordina el estado, router y componentes.
    """

    def __init__(self):
        self.state = get_state()
        self.router = get_router()
        self.initialized = False

    def setup_layout(self):
        """Crea el layout base de la aplicación."""
        app_container = document.getElementById("app-root")
        if not app_container:
            app_container = document.body

        # Limpiar contenedor
        app_container.innerHTML = ""

        # Crear estructura base
        layout = html.DIV(
            # Header/Navbar
            self._create_navbar() +

            # Contenedor principal (donde el router renderiza)
            html.MAIN(
                id="app",
                Class="container mx-auto px-4 py-6 min-h-screen"
            ) +

            # Footer
            self._create_footer(),

            Class="min-h-screen bg-gray-50"
        )

        app_container <= layout

    def _create_navbar(self):
        """Crea la barra de navegación."""
        state = self.state

        nav_items = [('home', 'Inicio', '🏠')]
        if feature_enabled('lessons'):
            nav_items.append(('lessons', 'Lecciones', '📚'))
        if feature_enabled('practice'):
            nav_items.append(('practice', 'Práctica', '✍️'))
        if feature_enabled('retrieval'):
            nav_items.append(('quiz', 'Repaso', '🧠'))
        if feature_enabled('puzzles'):
            nav_items.append(('puzzles', 'Puzzles', '🧩'))
        if feature_enabled('playground'):
            nav_items.append(('playground', 'Playground', '💻'))
        nav_items.append(('profile', 'Perfil', '👤'))

        def create_nav_link(route, label, icon_emoji):
            """Crea un enlace de navegación."""
            link = html.A(
                html.SPAN(icon_emoji, Class="text-lg") +
                html.SPAN(label, Class="ml-1 hidden sm:inline"),
                href=f"#{route}",
                Class="flex items-center px-3 py-2 rounded-lg text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            )
            return link

        # XP y nivel en el navbar
        level_info = state.get_level_info()
        progress_data = state.data.get('progress', {})
        current_xp = progress_data.get('xp', 0)
        streak_data = state.data.get('streak', {})
        streak = streak_data.get('current', 0)

        xp_display = html.DIV(
            html.DIV(
                html.SPAN("Nv." + str(level_info['level']), Class="font-bold text-indigo-600 mr-1") +
                html.SPAN(level_info['title'], Class="text-gray-500 text-sm hidden md:inline"),
                Class="flex items-center"
            ) +
            html.DIV(
                html.DIV(
                    Class="h-full bg-indigo-500 rounded-full transition-all",
                    style="width: " + str(level_info['progress']) + "%"
                ),
                Class="w-16 h-2 bg-gray-200 rounded-full overflow-hidden ml-2"
            ) +
            html.SPAN(str(current_xp) + " XP", Class="text-xs text-gray-500 ml-2"),
            Class="flex items-center",
            id="navbar-xp"
        )

        # Streak display
        streak_display = html.DIV(
            html.SPAN("🔥", Class="text-lg") +
            html.SPAN(str(streak), Class="font-bold text-orange-500"),
            Class="flex items-center gap-1",
            title="Racha: " + str(streak) + " días"
        )

        config = get_config()
        navbar = html.NAV(
            html.DIV(
                html.A(
                    html.SPAN(config['logo'], Class="text-2xl") +
                    html.SPAN(config['name'], Class="ml-2 text-xl font-bold text-gray-800"),
                    href="#home",
                    Class="flex items-center"
                ) +

                # Navigation links
                html.DIV(
                    [create_nav_link(route, label, icon) for route, label, icon in nav_items],
                    Class="flex items-center gap-1"
                ) +

                # User stats
                html.DIV(
                    streak_display + xp_display,
                    Class="flex items-center gap-4"
                ),

                Class="container mx-auto px-4 flex items-center justify-between"
            ),
            Class="bg-white shadow-sm py-3 sticky top-0 z-50"
        )

        return navbar

    def _create_footer(self):
        """Crea el pie de página."""
        config = get_config()
        return html.FOOTER(
            html.DIV(
                html.P(
                    config['name'] + " - " + config['tagline'],
                    Class="text-gray-500"
                ) +
                html.P(
                    config['footer'],
                    Class="text-gray-400 text-sm mt-1"
                ),
                Class="container mx-auto px-4 text-center"
            ),
            Class="bg-white border-t py-6 mt-12"
        )

    def setup_routes(self):
        """Configura las rutas de la aplicación."""
        from .pages import (
            home_page,
            lessons_page,
            lesson_detail_page,
            puzzles_page,
            puzzle_page,
            playground_page,
            profile_page,
            badges_page,
            assessment_page,
            practice_page,
            practice_exercise_page,
            final_project_page,
            quiz_page
        )

        router = self.router

        router.register('home', home_page, {'title': 'Inicio'})
        router.register('profile', profile_page, {'title': 'Mi Perfil'})
        router.register('badges', badges_page, {'title': 'Badges'})

        if feature_enabled('lessons'):
            router.register('lessons', lessons_page, {'title': 'Lecciones'})
            router.register('lesson/:id', lesson_detail_page, {'title': 'Lección'})
        if feature_enabled('puzzles'):
            router.register('puzzles', puzzles_page, {'title': 'Puzzles'})
            router.register('puzzle/:id', puzzle_page, {'title': 'Puzzle'})
        if feature_enabled('playground'):
            router.register('playground', playground_page, {'title': 'Playground'})
        if feature_enabled('assessment'):
            router.register('assessment', assessment_page, {'title': 'Evaluación Diagnóstica'})
        if feature_enabled('practice'):
            router.register('practice', practice_page, {'title': 'Práctica'})
            router.register('practice/:id', practice_exercise_page, {'title': 'Ejercicio de Práctica'})
        if feature_enabled('final_project'):
            router.register('final-project', final_project_page, {'title': 'Proyecto Final'})
        if feature_enabled('retrieval'):
            router.register('quiz', quiz_page, {'title': 'Quiz de Repaso'})

        # Hook para actualizar navbar después de navegación
        def update_navbar_stats(context):
            self._update_navbar_display()

        router.after_each(update_navbar_stats)

        # Página 404 personalizada
        router.on_not_found(self._not_found_page)

    def _update_navbar_display(self):
        """Actualiza el display del navbar con stats actuales."""
        state = self.state
        level_info = state.get_level_info()
        progress_data = state.data.get('progress', {})
        current_xp = progress_data.get('xp', 0)

        # Actualizar XP display
        xp_elem = document.getElementById("navbar-xp")
        if xp_elem:
            xp_elem.innerHTML = ""
            xp_elem <= html.DIV(
                html.SPAN("Nv." + str(level_info['level']), Class="font-bold text-indigo-600") +
                html.SPAN(" " + level_info['title'], Class="text-gray-500 text-sm hidden md:inline"),
                Class="flex items-center"
            )
            xp_elem <= html.DIV(
                html.DIV(
                    Class="h-full bg-indigo-500 rounded-full transition-all",
                    style="width: " + str(level_info['progress']) + "%"
                ),
                Class="w-20 h-2 bg-gray-200 rounded-full overflow-hidden"
            )
            xp_elem <= html.SPAN(str(current_xp) + " XP", Class="text-xs text-gray-500")

    def _not_found_page(self, path):
        """Página de error 404."""
        return html.DIV(
            html.DIV(
                html.SPAN("🔍", Class="text-6xl") +
                html.H1("Página no encontrada", Class="text-2xl font-bold mt-4 text-gray-700") +
                html.P(
                    "La ruta '" + str(path) + "' no existe en este curso.",
                    Class="text-gray-500 mt-2"
                ) +
                html.A(
                    "← Volver al inicio",
                    href="#home",
                    Class="inline-block mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                ),
                Class="text-center"
            ),
            Class="flex items-center justify-center min-h-96"
        )

    def init(self):
        """Inicializa la aplicación."""
        if self.initialized:
            return self

        # Actualizar streak al iniciar
        self.state.update_streak()

        # Crear layout
        self.setup_layout()

        # Configurar rutas
        self.setup_routes()

        # Iniciar router
        self.router.start("app")

        # Suscribirse a cambios de estado
        self.state.subscribe(self._on_state_change)

        self.initialized = True
        print("CWC initialized!")

        return self

    def _on_state_change(self, data):
        """Callback cuando cambia el estado."""
        self._update_navbar_display()


# Instancia global de la aplicación
_app_instance = None

def get_app():
    """Obtiene la instancia singleton de la aplicación."""
    global _app_instance
    if _app_instance is None:
        _app_instance = App()
    return _app_instance

def init_app():
    """Inicializa y retorna la aplicación."""
    return get_app().init()
