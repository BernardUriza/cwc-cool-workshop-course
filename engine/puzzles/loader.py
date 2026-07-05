# PromptCraft - Puzzle Loader
# Carga y gestión de puzzles

from browser import ajax, window
import json

# Cache de puzzles cargados
_puzzle_cache = {}

# Lista de puzzles disponibles (se carga dinámicamente)
_puzzle_index = None


def load_puzzle(puzzle_id, callback=None):
    """
    Carga un puzzle por su ID.

    Args:
        puzzle_id: ID del puzzle a cargar
        callback: Función a llamar con los datos del puzzle

    Returns:
        Datos del puzzle (si ya está en cache)
    """
    # Verificar cache
    if puzzle_id in _puzzle_cache:
        if callback:
            callback(_puzzle_cache[puzzle_id])
        return _puzzle_cache[puzzle_id]

    # Cargar desde archivo
    url = f"content/puzzles/{puzzle_id}.json"

    def on_complete(req):
        if req.status == 200:
            try:
                data = json.loads(req.text)
                _puzzle_cache[puzzle_id] = data
                if callback:
                    callback(data)
            except Exception as e:
                print(f"Error parsing puzzle {puzzle_id}: {e}")
                if callback:
                    callback(None)
        else:
            print(f"Error loading puzzle {puzzle_id}: {req.status}")
            if callback:
                callback(None)

    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('GET', url, True)
    req.send()

    return None


def load_all_puzzles(callback=None):
    """
    Carga el índice de todos los puzzles disponibles.

    Args:
        callback: Función a llamar con la lista de puzzles
    """
    global _puzzle_index

    if _puzzle_index is not None:
        if callback:
            callback(_puzzle_index)
        return _puzzle_index

    url = "content/puzzles/index.json"

    def on_complete(req):
        global _puzzle_index
        if req.status == 200:
            try:
                _puzzle_index = json.loads(req.text)
                if callback:
                    callback(_puzzle_index)
            except Exception as e:
                print(f"Error parsing puzzle index: {e}")
                _puzzle_index = get_default_puzzle_index()
                if callback:
                    callback(_puzzle_index)
        else:
            print(f"Error loading puzzle index: {req.status}")
            _puzzle_index = get_default_puzzle_index()
            if callback:
                callback(_puzzle_index)

    req = ajax.ajax()
    req.bind('complete', on_complete)
    req.open('GET', url, True)
    req.send()

    return None


def get_default_puzzle_index():
    """
    Retorna un índice de puzzles por defecto.
    Usado cuando no se puede cargar el archivo.
    """
    return {
        'puzzles': [
            {
                'id': 'intro-01',
                'title': 'El Primer Prompt',
                'description': 'Aprende los fundamentos del prompting con este puzzle introductorio.',
                'category': 'fundamentos',
                'difficulty': 1,
                'xp_reward': 50,
            },
            {
                'id': 'roles-01',
                'title': 'Maestro de Roles',
                'description': 'Descubre quién usó cada técnica de role-playing.',
                'category': 'tecnicas',
                'difficulty': 2,
                'xp_reward': 75,
            },
            {
                'id': 'chain-01',
                'title': 'Cadena de Pensamiento',
                'description': 'Resuelve el misterio del Chain of Thought.',
                'category': 'tecnicas',
                'difficulty': 3,
                'xp_reward': 100,
            },
        ],
        'categories': [
            {'id': 'fundamentos', 'name': 'Fundamentos', 'icon': '📚'},
            {'id': 'tecnicas', 'name': 'Técnicas', 'icon': '🎯'},
            {'id': 'avanzado', 'name': 'Avanzado', 'icon': '🚀'},
        ]
    }


def get_puzzle_by_id(puzzle_id):
    """
    Obtiene un puzzle del cache.

    Args:
        puzzle_id: ID del puzzle

    Returns:
        Datos del puzzle o None
    """
    return _puzzle_cache.get(puzzle_id)


def get_puzzles_by_category(category):
    """
    Obtiene puzzles filtrados por categoría.

    Args:
        category: Categoría a filtrar

    Returns:
        Lista de puzzles de esa categoría
    """
    if _puzzle_index is None:
        return []

    return [p for p in _puzzle_index.get('puzzles', [])
            if p.get('category') == category]


def get_puzzle_progress(puzzle_id, state):
    """
    Obtiene el progreso de un puzzle específico.

    Args:
        puzzle_id: ID del puzzle
        state: Estado de la aplicación

    Returns:
        Dict con información de progreso
    """
    puzzles_completed = state.data.get('puzzles_completed', {})
    puzzle_info = puzzles_completed.get(puzzle_id, {})

    return {
        'solved': puzzle_info.get('solved', False),
        'best_time': puzzle_info.get('best_time'),
        'best_stars': puzzle_info.get('best_stars', 0),
        'attempts': puzzle_info.get('attempts', 0),
    }


def mark_puzzle_solved(puzzle_id, result, state):
    """
    Marca un puzzle como resuelto y actualiza el estado.

    Args:
        puzzle_id: ID del puzzle
        result: Resultado de la resolución
        state: Estado de la aplicación
    """
    if 'puzzles_completed' not in state.data:
        state.data['puzzles_completed'] = {}

    current = state.data['puzzles_completed'].get(puzzle_id, {})

    # Actualizar solo si es mejor resultado
    best_time = current.get('best_time')
    if best_time is None or result['time'] < best_time:
        current['best_time'] = result['time']

    best_stars = current.get('best_stars', 0)
    if result['stars'] > best_stars:
        current['best_stars'] = result['stars']

    current['solved'] = True
    current['attempts'] = current.get('attempts', 0) + 1
    current['last_solved'] = str(window.Date.new())

    state.data['puzzles_completed'][puzzle_id] = current
    state.save()

    # Añadir XP
    state.add_xp(result['xp'], f"Puzzle: {puzzle_id}")

    return current


# Crear puzzles embebidos para desarrollo
EMBEDDED_PUZZLES = {
    'intro-01': {
        'id': 'intro-01',
        'title': 'El Primer Prompt',
        'description': 'Tres desarrolladores usaron diferentes técnicas de prompting. ¿Puedes descubrir quién usó cada una?',
        'difficulty': 1,
        'xp_reward': 50,
        'par_time': 180,
        'categories': [
            {'name': 'Personas', 'items': ['Ana', 'Bob', 'Carlos']},
            {'name': 'Técnicas', 'items': ['Zero-Shot', 'Few-Shot', 'CoT']},
            {'name': 'Resultados', 'items': ['Excelente', 'Bueno', 'Regular']}
        ],
        'clues': [
            "Ana no usó Few-Shot.",
            "El que usó Chain of Thought (CoT) obtuvo un resultado Excelente.",
            "Bob obtuvo un resultado Regular.",
            "Carlos no usó Zero-Shot.",
            "El que usó Zero-Shot obtuvo un resultado Bueno."
        ],
        'hints': [
            "Empieza por la pista 2: relaciona CoT con Excelente.",
            "La pista 5 te dice que Zero-Shot → Bueno.",
            "Si Bob tuvo Regular y Zero-Shot dio Bueno, Bob no usó Zero-Shot."
        ],
        'solution': {
            'Personas__Técnicas': {
                '0,1': 'check',  # Ana - Few-Shot (incorrecto según pista 1, ajustar)
                '1,0': 'check',  # Bob - Zero-Shot
                '2,2': 'check'   # Carlos - CoT
            },
            'Personas__Resultados': {
                '0,1': 'check',  # Ana - Bueno
                '1,2': 'check',  # Bob - Regular
                '2,0': 'check'   # Carlos - Excelente
            },
            'Técnicas__Resultados': {
                '0,1': 'check',  # Zero-Shot - Bueno
                '1,2': 'check',  # Few-Shot - Regular
                '2,0': 'check'   # CoT - Excelente
            }
        }
    },
    'roles-01': {
        'id': 'roles-01',
        'title': 'Maestro de Roles',
        'description': 'Cuatro expertos en IA usaron diferentes roles para sus prompts. Descubre las combinaciones.',
        'difficulty': 2,
        'xp_reward': 75,
        'par_time': 300,
        'categories': [
            {'name': 'Expertos', 'items': ['Diana', 'Elena', 'Fran', 'Gloria']},
            {'name': 'Roles', 'items': ['Profesor', 'Revisor', 'Asistente', 'Experto']},
            {'name': 'Tareas', 'items': ['Código', 'Texto', 'Datos', 'Diseño']}
        ],
        'clues': [
            "Diana usó el rol de Profesor.",
            "El que trabajó con Código usó el rol de Revisor.",
            "Elena no trabajó con Texto ni Diseño.",
            "Gloria usó el rol de Asistente.",
            "Fran trabajó con Diseño.",
            "El Experto trabajó con Datos."
        ],
        'hints': [
            "Empieza conectando Diana con Profesor (pista 1).",
            "Gloria es Asistente (pista 4), así que no es Revisor.",
            "Si Fran trabaja con Diseño y el Revisor trabaja con Código, Fran no es Revisor."
        ],
        'solution': {
            'Expertos__Roles': {
                '0,0': 'check',  # Diana - Profesor
                '1,3': 'check',  # Elena - Experto
                '2,1': 'check',  # Fran - Revisor
                '3,2': 'check'   # Gloria - Asistente
            }
        }
    }
}


def get_embedded_puzzle(puzzle_id):
    """Obtiene un puzzle embebido."""
    return EMBEDDED_PUZZLES.get(puzzle_id)
