# PromptCraft - Router Module
# Sistema de navegación SPA basado en hash

from browser import window, document, html

class Router:
    """
    Sistema de routing SPA basado en hash.
    Maneja navegación entre páginas sin recargar.
    """

    def __init__(self):
        self.routes = {}
        self.current_route = None
        self.current_params = {}
        self.before_hooks = []
        self.after_hooks = []
        self.not_found_handler = None
        self.container_id = "app"

    def register(self, path, handler, meta=None):
        """
        Registra una ruta con su handler.

        Args:
            path: Ruta (ej: 'home', 'lesson/:id', 'puzzle/:category/:id')
            handler: Función que retorna el contenido de la página
            meta: Metadatos opcionales (title, requires_auth, etc.)
        """
        self.routes[path] = {
            'handler': handler,
            'meta': meta or {}
        }
        return self

    def before_each(self, hook):
        """Registra un hook que se ejecuta antes de cada navegación."""
        self.before_hooks.append(hook)
        return self

    def after_each(self, hook):
        """Registra un hook que se ejecuta después de cada navegación."""
        self.after_hooks.append(hook)
        return self

    def on_not_found(self, handler):
        """Registra handler para rutas no encontradas."""
        self.not_found_handler = handler
        return self

    def parse_hash(self, hash_str):
        """
        Parsea el hash URL y extrae ruta y parámetros.

        Ejemplos:
            '#home' -> ('home', {})
            '#lesson/1' -> ('lesson/:id', {'id': '1'})
            '#puzzle/logic/3' -> ('puzzle/:category/:id', {'category': 'logic', 'id': '3'})
        """
        # Remover # inicial
        if hash_str.startswith('#'):
            hash_str = hash_str[1:]

        if not hash_str:
            return 'home', {}

        parts = hash_str.split('/')

        # Buscar ruta que coincida
        for route_path in self.routes:
            route_parts = route_path.split('/')

            if len(route_parts) != len(parts):
                continue

            params = {}
            match = True

            for i, (route_part, url_part) in enumerate(zip(route_parts, parts)):
                if route_part.startswith(':'):
                    # Parámetro dinámico
                    param_name = route_part[1:]
                    params[param_name] = url_part
                elif route_part != url_part:
                    match = False
                    break

            if match:
                return route_path, params

        # No se encontró ruta
        return None, {}

    def navigate(self, path, params=None):
        """
        Navega a una ruta programáticamente.

        Args:
            path: Ruta destino (ej: 'lesson/:id' o 'lessons')
            params: Dict de parámetros (ej: {'id': '5'})
        """
        if params:
            # Construir URL con parámetros
            url_parts = []
            for part in path.split('/'):
                if part.startswith(':'):
                    param_name = part[1:]
                    url_parts.append(str(params.get(param_name, '')))
                else:
                    url_parts.append(part)
            path = '/'.join(url_parts)

        window.location.hash = path

    def go_back(self):
        """Navega hacia atrás en el historial."""
        window.history.back()

    def go_forward(self):
        """Navega hacia adelante en el historial."""
        window.history.forward()

    def handle_route_change(self, event=None):
        """Maneja el cambio de ruta (evento hashchange)."""
        hash_str = window.location.hash
        route_path, params = self.parse_hash(hash_str)

        # Ejecutar hooks before
        context = {
            'from': self.current_route,
            'to': route_path,
            'params': params
        }

        for hook in self.before_hooks:
            result = hook(context)
            if result is False:
                # Hook canceló la navegación
                return

        self.current_route = route_path
        self.current_params = params

        # Obtener contenedor
        container = document.getElementById(self.container_id)
        if not container:
            print(f"Error: Container '{self.container_id}' not found")
            return

        # Limpiar contenedor
        container.innerHTML = ""

        if route_path and route_path in self.routes:
            # Ejecutar handler de la ruta
            route_info = self.routes[route_path]

            # Actualizar título si está definido
            if 'title' in route_info['meta']:
                document.title = f"PromptCraft - {route_info['meta']['title']}"

            try:
                content = route_info['handler'](params)
                if content:
                    container <= content
            except Exception as e:
                print(f"Error rendering route '{route_path}': {e}")
                container <= html.DIV(
                    html.H2("Error al cargar la página") +
                    html.P(str(e)),
                    Class="text-center py-12 text-red-500"
                )
        else:
            # Ruta no encontrada
            if self.not_found_handler:
                content = self.not_found_handler(hash_str)
                if content:
                    container <= content
            else:
                container <= self._default_not_found(hash_str)

        # Ejecutar hooks after
        for hook in self.after_hooks:
            hook(context)

        # Scroll al inicio
        window.scrollTo(0, 0)

    def _default_not_found(self, path):
        """Página 404 por defecto."""
        return html.DIV(
            html.DIV(
                html.SPAN("404", Class="text-8xl font-bold text-gray-300") +
                html.H1("Página no encontrada", Class="text-2xl font-bold mt-4 text-gray-700") +
                html.P(f"La ruta '{path}' no existe.", Class="text-gray-500 mt-2") +
                html.BUTTON(
                    "Ir al inicio",
                    Class="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                ),
                Class="text-center"
            ),
            Class="flex items-center justify-center min-h-96"
        )

    def start(self, container_id="app"):
        """
        Inicia el router y escucha cambios de hash.

        Args:
            container_id: ID del elemento donde se renderiza el contenido
        """
        self.container_id = container_id

        # Bind al evento hashchange
        window.bind('hashchange', self.handle_route_change)

        # Manejar ruta inicial
        self.handle_route_change()

        return self

    def stop(self):
        """Detiene el router."""
        window.unbind('hashchange', self.handle_route_change)


# Instancia global del router
_router_instance = None

def get_router():
    """Obtiene la instancia singleton del router."""
    global _router_instance
    if _router_instance is None:
        _router_instance = Router()
    return _router_instance

def navigate(path, params=None):
    """Atajo para navegar."""
    get_router().navigate(path, params)

def current_route():
    """Obtiene la ruta actual."""
    router = get_router()
    return router.current_route, router.current_params


# Decorador para registrar rutas
def route(path, meta=None):
    """
    Decorador para registrar rutas.

    Uso:
        @route('home', meta={'title': 'Inicio'})
        def home_page(params):
            return html.DIV("Página de inicio")
    """
    def decorator(func):
        get_router().register(path, func, meta)
        return func
    return decorator
