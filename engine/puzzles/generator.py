# PromptCraft - Puzzle Generator
# Generador de puzzles aleatorios

import random


def generate_puzzle(config=None):
    """
    Genera un puzzle de lógica aleatorio.

    Args:
        config: Configuración del puzzle
            - num_categories: Número de categorías (2-4)
            - items_per_category: Items por categoría (3-5)
            - difficulty: 1-5
            - theme: Tema del puzzle

    Returns:
        Dict con el puzzle generado
    """
    config = config or {}

    num_categories = config.get('num_categories', 3)
    items_per_category = config.get('items_per_category', 3)
    difficulty = config.get('difficulty', 2)
    theme = config.get('theme', 'prompt_engineering')

    # Obtener templates según el tema
    templates = PUZZLE_TEMPLATES.get(theme, PUZZLE_TEMPLATES['prompt_engineering'])

    # Seleccionar categorías aleatorias
    categories = random.sample(templates['categories'], min(num_categories, len(templates['categories'])))

    # Seleccionar items para cada categoría
    puzzle_categories = []
    for cat in categories:
        items = random.sample(cat['items'], min(items_per_category, len(cat['items'])))
        puzzle_categories.append({
            'name': cat['name'],
            'items': items
        })

    # Generar solución aleatoria
    solution = generate_solution(puzzle_categories)

    # Generar pistas basadas en la solución
    clues = generate_clues(puzzle_categories, solution, difficulty)

    # Generar hints
    hints = generate_hints(puzzle_categories, solution, clues)

    # Calcular XP basado en dificultad
    xp_reward = 25 + (difficulty * 25) + (items_per_category * 10)

    return {
        'id': f'generated-{random.randint(1000, 9999)}',
        'title': random.choice(templates['titles']),
        'description': random.choice(templates['descriptions']),
        'difficulty': difficulty,
        'xp_reward': xp_reward,
        'par_time': 120 + (difficulty * 60) + (items_per_category * 30),
        'categories': puzzle_categories,
        'clues': clues,
        'hints': hints,
        'solution': solution,
        'generated': True
    }


def generate_solution(categories):
    """
    Genera una solución válida para el puzzle.
    Cada item de una categoría se relaciona exactamente con uno de cada otra categoría.
    """
    solution = {}
    n = len(categories[0]['items'])

    # Crear permutaciones para cada par de categorías
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            cat1 = categories[i]
            cat2 = categories[j]
            grid_key = f"{cat1['name']}__{cat2['name']}"

            # Generar permutación aleatoria
            perm = list(range(n))
            random.shuffle(perm)

            grid = {}
            for row, col in enumerate(perm):
                grid[(row, col)] = 'check'

            solution[grid_key] = grid

    return solution


def generate_clues(categories, solution, difficulty):
    """
    Genera pistas basadas en la solución.
    Más dificultad = menos pistas directas.
    """
    clues = []
    n = len(categories[0]['items'])

    # Número de pistas directas basado en dificultad
    direct_clues = max(1, n - difficulty)
    negative_clues = difficulty

    # Generar pistas directas
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            cat1 = categories[i]
            cat2 = categories[j]
            grid_key = f"{cat1['name']}__{cat2['name']}"

            for (row, col), state in solution[grid_key].items():
                if state == 'check' and len(clues) < direct_clues:
                    item1 = cat1['items'][row]
                    item2 = cat2['items'][col]
                    clue = generate_clue_text('direct', item1, item2, cat1['name'], cat2['name'])
                    clues.append(clue)

    # Generar pistas negativas
    for _ in range(negative_clues):
        # Seleccionar par de categorías aleatorio
        i, j = random.sample(range(len(categories)), 2)
        if i > j:
            i, j = j, i

        cat1 = categories[i]
        cat2 = categories[j]
        grid_key = f"{cat1['name']}__{cat2['name']}"

        # Encontrar una relación que NO sea correcta
        for row in range(n):
            for col in range(n):
                if solution[grid_key].get((row, col)) != 'check':
                    item1 = cat1['items'][row]
                    item2 = cat2['items'][col]
                    clue = generate_clue_text('not', item1, item2, cat1['name'], cat2['name'])
                    clues.append(clue)
                    break
            else:
                continue
            break

    random.shuffle(clues)
    return clues


def generate_clue_text(clue_type, item1, item2, cat1_name, cat2_name):
    """Genera el texto de una pista."""
    if clue_type == 'direct':
        templates = [
            f"{item1} usa {item2}.",
            f"{item1} está asociado con {item2}.",
            f"{item1} eligió {item2}.",
            f"A {item1} le corresponde {item2}."
        ]
    else:  # 'not'
        templates = [
            f"{item1} no usa {item2}.",
            f"{item1} no está asociado con {item2}.",
            f"{item1} no eligió {item2}.",
            f"A {item1} no le corresponde {item2}."
        ]

    return random.choice(templates)


def generate_hints(categories, solution, clues):
    """Genera hints progresivos."""
    hints = [
        "Empieza identificando las relaciones directas de las pistas.",
        "Usa eliminación: si algo no puede ser X, márcalo con ✗.",
        "Cuando solo quede una opción en una fila o columna, esa debe ser la correcta."
    ]

    return hints


# Templates de puzzles por tema
PUZZLE_TEMPLATES = {
    'prompt_engineering': {
        'titles': [
            'El Misterio del Prompt Perfecto',
            'Técnicas en Acción',
            'El Desafío del Prompting',
            'Roles y Resultados',
        ],
        'descriptions': [
            'Descubre las combinaciones correctas de técnicas y resultados.',
            'Varios expertos usaron diferentes técnicas. ¿Puedes descifrar quién usó cada una?',
            'Analiza las pistas y deduce las relaciones correctas.',
        ],
        'categories': [
            {
                'name': 'Personas',
                'items': ['Ana', 'Bob', 'Carlos', 'Diana', 'Elena']
            },
            {
                'name': 'Técnicas',
                'items': ['Zero-Shot', 'Few-Shot', 'Chain of Thought', 'Role-Playing', 'Iterativo']
            },
            {
                'name': 'Modelos',
                'items': ['GPT-4', 'Claude', 'Gemini', 'Llama', 'Mistral']
            },
            {
                'name': 'Resultados',
                'items': ['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Mejorable']
            },
            {
                'name': 'Tareas',
                'items': ['Código', 'Resumen', 'Análisis', 'Creativo', 'Traducción']
            }
        ]
    },
    'ai_basics': {
        'titles': [
            'Conceptos de IA',
            'El Mundo de la IA',
        ],
        'descriptions': [
            'Relaciona conceptos fundamentales de inteligencia artificial.',
        ],
        'categories': [
            {
                'name': 'Conceptos',
                'items': ['Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision']
            },
            {
                'name': 'Aplicaciones',
                'items': ['Chatbots', 'Reconocimiento', 'Predicción', 'Generación']
            },
            {
                'name': 'Compañías',
                'items': ['OpenAI', 'Anthropic', 'Google', 'Meta']
            }
        ]
    }
}
