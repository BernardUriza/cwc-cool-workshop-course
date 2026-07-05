# PromptCraft - Level System
# Sistema de niveles

# Umbrales de XP para cada nivel
LEVEL_THRESHOLDS = [
    0,       # Nivel 1: 0 XP
    100,     # Nivel 2: 100 XP
    350,     # Nivel 3: 350 XP
    850,     # Nivel 4: 850 XP
    1600,    # Nivel 5: 1600 XP
    2600,    # Nivel 6: 2600 XP
    4100,    # Nivel 7: 4100 XP
    6100,    # Nivel 8: 6100 XP
    9100,    # Nivel 9: 9100 XP
    14100,   # Nivel 10: 14100 XP
    20000,   # Nivel 11+ (máximo práctico)
]

# Títulos por nivel
LEVEL_TITLES = {
    1: 'Novato',
    2: 'Aprendiz',
    3: 'Estudiante',
    4: 'Practicante',
    5: 'Competente',
    6: 'Hábil',
    7: 'Experto',
    8: 'Maestro',
    9: 'Gran Maestro',
    10: 'Leyenda',
}

# Iconos por nivel
LEVEL_ICONS = {
    1: '🌱',
    2: '🌿',
    3: '🌳',
    4: '⭐',
    5: '🌟',
    6: '💫',
    7: '🔥',
    8: '👑',
    9: '💎',
    10: '🏆',
}

# Colores por nivel (para UI)
LEVEL_COLORS = {
    1: {'primary': '#9CA3AF', 'secondary': '#D1D5DB'},  # Gray
    2: {'primary': '#22C55E', 'secondary': '#86EFAC'},  # Green
    3: {'primary': '#3B82F6', 'secondary': '#93C5FD'},  # Blue
    4: {'primary': '#8B5CF6', 'secondary': '#C4B5FD'},  # Purple
    5: {'primary': '#F59E0B', 'secondary': '#FCD34D'},  # Amber
    6: {'primary': '#F97316', 'secondary': '#FDBA74'},  # Orange
    7: {'primary': '#EF4444', 'secondary': '#FCA5A5'},  # Red
    8: {'primary': '#EC4899', 'secondary': '#F9A8D4'},  # Pink
    9: {'primary': '#6366F1', 'secondary': '#A5B4FC'},  # Indigo
    10: {'primary': '#EAB308', 'secondary': '#FDE047'}, # Yellow/Gold
}


class LevelSystem:
    """
    Sistema de niveles basado en XP.
    """

    def __init__(self, state=None):
        self.state = state

    def get_level(self, xp):
        """
        Obtiene el nivel para una cantidad de XP.

        Args:
            xp: Cantidad de XP

        Returns:
            Número de nivel (1-10+)
        """
        level = 1
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if xp >= threshold:
                level = i + 1
            else:
                break
        return min(level, 10)

    def get_info(self, xp):
        """
        Obtiene información completa del nivel.

        Args:
            xp: Cantidad de XP

        Returns:
            Dict con información del nivel
        """
        level = self.get_level(xp)
        title = get_level_title(level)
        icon = get_level_icon(level)
        colors = LEVEL_COLORS.get(level, LEVEL_COLORS[1])

        # Calcular progreso hacia siguiente nivel
        current_threshold = LEVEL_THRESHOLDS[level - 1] if level <= len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
        next_threshold = LEVEL_THRESHOLDS[level] if level < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]

        xp_in_level = xp - current_threshold
        xp_for_next = next_threshold - current_threshold

        if xp_for_next > 0:
            progress = min(100, (xp_in_level / xp_for_next) * 100)
        else:
            progress = 100

        return {
            'level': level,
            'title': title,
            'icon': icon,
            'colors': colors,
            'xp_in_level': xp_in_level,
            'xp_for_next': xp_for_next,
            'progress': progress,
            'is_max': level >= 10,
            'next_title': get_level_title(min(level + 1, 10)) if level < 10 else None,
        }

    def xp_needed_for_level(self, target_level):
        """
        Calcula XP necesario para alcanzar un nivel.

        Args:
            target_level: Nivel objetivo

        Returns:
            XP necesario
        """
        if target_level <= 1:
            return 0
        if target_level > len(LEVEL_THRESHOLDS):
            return LEVEL_THRESHOLDS[-1]
        return LEVEL_THRESHOLDS[target_level - 1]

    def get_all_levels(self):
        """
        Obtiene información de todos los niveles.

        Returns:
            Lista de dicts con información de cada nivel
        """
        levels = []
        for i in range(1, 11):
            levels.append({
                'level': i,
                'title': get_level_title(i),
                'icon': get_level_icon(i),
                'xp_required': LEVEL_THRESHOLDS[i - 1] if i <= len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1],
                'colors': LEVEL_COLORS.get(i, LEVEL_COLORS[1]),
            })
        return levels


def get_level_title(level):
    """Obtiene el título para un nivel."""
    return LEVEL_TITLES.get(level, 'Leyenda')


def get_level_icon(level):
    """Obtiene el ícono para un nivel."""
    return LEVEL_ICONS.get(level, '🏆')


def get_level_info(xp):
    """
    Helper para obtener info de nivel.

    Args:
        xp: Cantidad de XP

    Returns:
        Dict con información del nivel
    """
    return LevelSystem().get_info(xp)


def get_level_color(level):
    """Obtiene los colores para un nivel."""
    return LEVEL_COLORS.get(level, LEVEL_COLORS[1])
