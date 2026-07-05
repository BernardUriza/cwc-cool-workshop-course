# PromptCraft - Badge System
# Sistema de badges/logros

from browser import window
from ..components.toast import badge_toast


# Definición de todos los badges
BADGES = {
    # === Badges de Progreso ===
    'first_lesson': {
        'id': 'first_lesson',
        'name': 'Primera Lección',
        'description': 'Completa tu primera lección',
        'icon': '📖',
        'rarity': 'common',
        'category': 'progress',
        'condition': {'type': 'lessons_completed', 'value': 1},
    },
    'lesson_5': {
        'id': 'lesson_5',
        'name': 'Estudiante Dedicado',
        'description': 'Completa 5 lecciones',
        'icon': '📚',
        'rarity': 'common',
        'category': 'progress',
        'condition': {'type': 'lessons_completed', 'value': 5},
    },
    'lesson_10': {
        'id': 'lesson_10',
        'name': 'Conocimiento Sólido',
        'description': 'Completa 10 lecciones',
        'icon': '🎓',
        'rarity': 'rare',
        'category': 'progress',
        'condition': {'type': 'lessons_completed', 'value': 10},
    },
    'lesson_20': {
        'id': 'lesson_20',
        'name': 'Erudito del Prompting',
        'description': 'Completa todas las lecciones',
        'icon': '🏛️',
        'rarity': 'legendary',
        'category': 'progress',
        'condition': {'type': 'lessons_completed', 'value': 20},
    },

    # === Badges de Puzzles ===
    'first_puzzle': {
        'id': 'first_puzzle',
        'name': 'Primer Puzzle',
        'description': 'Resuelve tu primer puzzle',
        'icon': '🧩',
        'rarity': 'common',
        'category': 'puzzles',
        'condition': {'type': 'puzzles_solved', 'value': 1},
    },
    'puzzle_5': {
        'id': 'puzzle_5',
        'name': 'Mente Lógica',
        'description': 'Resuelve 5 puzzles',
        'icon': '🧠',
        'rarity': 'common',
        'category': 'puzzles',
        'condition': {'type': 'puzzles_solved', 'value': 5},
    },
    'puzzle_10': {
        'id': 'puzzle_10',
        'name': 'Maestro de Puzzles',
        'description': 'Resuelve 10 puzzles',
        'icon': '🎯',
        'rarity': 'rare',
        'category': 'puzzles',
        'condition': {'type': 'puzzles_solved', 'value': 10},
    },
    'puzzle_perfect': {
        'id': 'puzzle_perfect',
        'name': 'Perfección',
        'description': 'Resuelve un puzzle con 3 estrellas',
        'icon': '⭐',
        'rarity': 'rare',
        'category': 'puzzles',
        'condition': {'type': 'puzzle_stars', 'value': 3},
    },
    'puzzle_no_hints': {
        'id': 'puzzle_no_hints',
        'name': 'Sin Ayuda',
        'description': 'Resuelve un puzzle sin usar pistas',
        'icon': '💪',
        'rarity': 'rare',
        'category': 'puzzles',
        'condition': {'type': 'puzzle_no_hints', 'value': True},
    },
    'puzzle_speed': {
        'id': 'puzzle_speed',
        'name': 'Velocidad Mental',
        'description': 'Resuelve un puzzle en menos de 2 minutos',
        'icon': '⚡',
        'rarity': 'epic',
        'category': 'puzzles',
        'condition': {'type': 'puzzle_time', 'value': 120},
    },

    # === Badges de Racha ===
    'streak_3': {
        'id': 'streak_3',
        'name': 'Constancia',
        'description': 'Mantén una racha de 3 días',
        'icon': '🔥',
        'rarity': 'common',
        'category': 'streak',
        'condition': {'type': 'streak', 'value': 3},
    },
    'streak_7': {
        'id': 'streak_7',
        'name': 'Semana Perfecta',
        'description': 'Mantén una racha de 7 días',
        'icon': '📅',
        'rarity': 'rare',
        'category': 'streak',
        'condition': {'type': 'streak', 'value': 7},
    },
    'streak_30': {
        'id': 'streak_30',
        'name': 'Mes de Fuego',
        'description': 'Mantén una racha de 30 días',
        'icon': '🌋',
        'rarity': 'epic',
        'category': 'streak',
        'condition': {'type': 'streak', 'value': 30},
    },
    'streak_100': {
        'id': 'streak_100',
        'name': 'Imparable',
        'description': 'Mantén una racha de 100 días',
        'icon': '💯',
        'rarity': 'legendary',
        'category': 'streak',
        'condition': {'type': 'streak', 'value': 100},
    },

    # === Badges de XP/Nivel ===
    'xp_100': {
        'id': 'xp_100',
        'name': 'Primeros Pasos',
        'description': 'Acumula 100 XP',
        'icon': '🌱',
        'rarity': 'common',
        'category': 'xp',
        'condition': {'type': 'xp', 'value': 100},
    },
    'xp_1000': {
        'id': 'xp_1000',
        'name': 'Millar',
        'description': 'Acumula 1,000 XP',
        'icon': '💎',
        'rarity': 'rare',
        'category': 'xp',
        'condition': {'type': 'xp', 'value': 1000},
    },
    'xp_5000': {
        'id': 'xp_5000',
        'name': 'Potencia',
        'description': 'Acumula 5,000 XP',
        'icon': '🚀',
        'rarity': 'epic',
        'category': 'xp',
        'condition': {'type': 'xp', 'value': 5000},
    },
    'level_5': {
        'id': 'level_5',
        'name': 'Competente',
        'description': 'Alcanza el nivel 5',
        'icon': '🌟',
        'rarity': 'rare',
        'category': 'xp',
        'condition': {'type': 'level', 'value': 5},
    },
    'level_10': {
        'id': 'level_10',
        'name': 'Leyenda',
        'description': 'Alcanza el nivel máximo',
        'icon': '🏆',
        'rarity': 'legendary',
        'category': 'xp',
        'condition': {'type': 'level', 'value': 10},
    },

    # === Badges de Técnicas ===
    'technique_zeroshot': {
        'id': 'technique_zeroshot',
        'name': 'Zero-Shot Master',
        'description': 'Completa la lección de Zero-Shot',
        'icon': '🎯',
        'rarity': 'common',
        'category': 'techniques',
        'condition': {'type': 'lesson_complete', 'value': 'zero-shot'},
    },
    'technique_fewshot': {
        'id': 'technique_fewshot',
        'name': 'Few-Shot Expert',
        'description': 'Completa la lección de Few-Shot',
        'icon': '📋',
        'rarity': 'common',
        'category': 'techniques',
        'condition': {'type': 'lesson_complete', 'value': 'few-shot'},
    },
    'technique_cot': {
        'id': 'technique_cot',
        'name': 'Pensador en Cadena',
        'description': 'Completa la lección de Chain of Thought',
        'icon': '🔗',
        'rarity': 'rare',
        'category': 'techniques',
        'condition': {'type': 'lesson_complete', 'value': 'chain-of-thought'},
    },
    'technique_all': {
        'id': 'technique_all',
        'name': 'Arsenal Completo',
        'description': 'Domina todas las técnicas principales',
        'icon': '🎖️',
        'rarity': 'epic',
        'category': 'techniques',
        'condition': {'type': 'all_techniques', 'value': True},
    },

    # === Badges de Claude Code ===
    'claude_apprentice': {
        'id': 'claude_apprentice',
        'name': 'Aprendiz de Claude',
        'description': 'Completa tu primera lección de Claude Code',
        'icon': '🤖',
        'rarity': 'common',
        'category': 'claude-code',
        'condition': {'type': 'lesson_complete', 'value': 'claude-code-intro'},
    },
    'claude_navigator': {
        'id': 'claude_navigator',
        'name': 'Navegante de Código',
        'description': 'Aprende a navegar proyectos con Claude Code',
        'icon': '🧭',
        'rarity': 'common',
        'category': 'claude-code',
        'condition': {'type': 'lesson_complete', 'value': 'claude-code-navigation'},
    },
    'claude_debugger': {
        'id': 'claude_debugger',
        'name': 'Cazador de Bugs',
        'description': 'Domina el debugging con Claude Code',
        'icon': '🐛',
        'rarity': 'rare',
        'category': 'claude-code',
        'condition': {'type': 'lesson_complete', 'value': 'claude-code-debugging'},
    },
    'claude_master': {
        'id': 'claude_master',
        'name': 'Maestro de Claude Code',
        'description': 'Completa todas las lecciones de Claude Code',
        'icon': '🎓',
        'rarity': 'epic',
        'category': 'claude-code',
        'condition': {'type': 'all_claude_lessons', 'value': True},
    },
    'claude_puzzle_solver': {
        'id': 'claude_puzzle_solver',
        'name': 'Rompecabezas IA',
        'description': 'Resuelve todos los puzzles de Claude Code',
        'icon': '🧩',
        'rarity': 'rare',
        'category': 'claude-code',
        'condition': {'type': 'all_claude_puzzles', 'value': True},
    },

    # === Badges Especiales ===
    'early_bird': {
        'id': 'early_bird',
        'name': 'Madrugador',
        'description': 'Practica antes de las 7 AM',
        'icon': '🌅',
        'rarity': 'rare',
        'category': 'special',
        'condition': {'type': 'time_of_day', 'value': 'early'},
    },
    'night_owl': {
        'id': 'night_owl',
        'name': 'Búho Nocturno',
        'description': 'Practica después de medianoche',
        'icon': '🦉',
        'rarity': 'rare',
        'category': 'special',
        'condition': {'type': 'time_of_day', 'value': 'night'},
    },
    'explorer': {
        'id': 'explorer',
        'name': 'Explorador',
        'description': 'Usa el Playground por primera vez',
        'icon': '🧭',
        'rarity': 'common',
        'category': 'special',
        'condition': {'type': 'playground_use', 'value': 1},
    },
    'completionist': {
        'id': 'completionist',
        'name': 'Completista',
        'description': 'Desbloquea todos los badges',
        'icon': '👑',
        'rarity': 'legendary',
        'category': 'special',
        'condition': {'type': 'all_badges', 'value': True},
    },

    # === Badge de Graduación ===
    'graduate': {
        'id': 'graduate',
        'name': 'Graduado de PromptCraft',
        'description': 'Completa el Proyecto Final del curso',
        'icon': '🎓',
        'rarity': 'legendary',
        'category': 'achievement',
        'condition': {'type': 'project_complete', 'value': True},
    },
    'practice_master': {
        'id': 'practice_master',
        'name': 'Maestro de la Práctica',
        'description': 'Completa todos los ejercicios de práctica',
        'icon': '✍️',
        'rarity': 'epic',
        'category': 'achievement',
        'condition': {'type': 'all_practice', 'value': True},
    },
    'assessment_complete': {
        'id': 'assessment_complete',
        'name': 'Autoconocimiento',
        'description': 'Completa la evaluación diagnóstica',
        'icon': '📊',
        'rarity': 'common',
        'category': 'achievement',
        'condition': {'type': 'assessment_complete', 'value': True},
    },
}


class BadgeManager:
    """
    Gestiona los badges del usuario.
    """

    def __init__(self, state):
        self.state = state

    def get_all(self, include_locked=True):
        """
        Obtiene todos los badges.

        Args:
            include_locked: Incluir badges no desbloqueados

        Returns:
            Lista de badges con estado
        """
        unlocked = set(self.state.data.get('badges', []))
        badges = []

        for badge_id, badge_data in BADGES.items():
            badge = dict(badge_data)
            badge['unlocked'] = badge_id in unlocked

            if badge['unlocked']:
                badge['unlocked_at'] = self._get_unlock_time(badge_id)

            if include_locked or badge['unlocked']:
                badges.append(badge)

        return badges

    def get_unlocked(self):
        """Obtiene solo badges desbloqueados."""
        return self.get_all(include_locked=False)

    def get_by_category(self, category):
        """Obtiene badges de una categoría."""
        return [b for b in self.get_all() if b.get('category') == category]

    def get_by_rarity(self, rarity):
        """Obtiene badges de una rareza."""
        return [b for b in self.get_all() if b.get('rarity') == rarity]

    def _get_unlock_time(self, badge_id):
        """Obtiene cuándo se desbloqueó un badge."""
        history = self.state.data.get('badge_history', {})
        return history.get(badge_id)

    def unlock(self, badge_id, show_toast=True):
        """
        Desbloquea un badge.

        Args:
            badge_id: ID del badge
            show_toast: Mostrar notificación

        Returns:
            Badge desbloqueado o None si ya estaba
        """
        if badge_id not in BADGES:
            return None

        badges = set(self.state.data.get('badges', []))
        if badge_id in badges:
            return None  # Ya desbloqueado

        # Desbloquear
        badges.add(badge_id)
        self.state.data['badges'] = list(badges)

        # Registrar tiempo
        if 'badge_history' not in self.state.data:
            self.state.data['badge_history'] = {}
        self.state.data['badge_history'][badge_id] = str(window.Date.new())

        self.state.save()

        badge = BADGES[badge_id]

        if show_toast:
            badge_toast(badge['name'], badge['icon'])

        return badge

    def check_and_unlock(self, condition_type, value):
        """
        Verifica y desbloquea badges basados en una condición.

        Args:
            condition_type: Tipo de condición
            value: Valor actual

        Returns:
            Lista de badges desbloqueados
        """
        unlocked = []

        for badge_id, badge in BADGES.items():
            condition = badge.get('condition', {})

            if condition.get('type') != condition_type:
                continue

            target = condition.get('value')

            # Verificar si cumple la condición
            meets_condition = False

            if isinstance(target, bool):
                meets_condition = value == target
            elif isinstance(target, (int, float)):
                if condition_type in ['puzzle_time']:
                    # Para tiempo, menor es mejor
                    meets_condition = value <= target
                else:
                    meets_condition = value >= target
            elif isinstance(target, str):
                meets_condition = value == target

            if meets_condition:
                result = self.unlock(badge_id)
                if result:
                    unlocked.append(result)

        return unlocked

    def get_progress(self, badge_id):
        """
        Obtiene el progreso hacia un badge.

        Args:
            badge_id: ID del badge

        Returns:
            Dict con current, target, y percentage
        """
        if badge_id not in BADGES:
            return None

        badge = BADGES[badge_id]
        condition = badge.get('condition', {})
        condition_type = condition.get('type')
        target = condition.get('value')

        current = 0

        # Obtener valor actual según tipo
        if condition_type == 'lessons_completed':
            current = len(self.state.data.get('lessons_completed', []))
        elif condition_type == 'puzzles_solved':
            current = len(self.state.data.get('puzzles_completed', {}))
        elif condition_type == 'streak':
            current = self.state.data.get('streak', {}).get('current', 0)
        elif condition_type == 'xp':
            current = self.state.data.get('xp', 0)
        elif condition_type == 'level':
            from .levels import LevelSystem
            current = LevelSystem().get_level(self.state.data.get('xp', 0))

        if isinstance(target, (int, float)) and target > 0:
            percentage = min(100, (current / target) * 100)
        else:
            percentage = 100 if current else 0

        return {
            'current': current,
            'target': target,
            'percentage': percentage,
        }

    def get_stats(self):
        """Obtiene estadísticas de badges."""
        all_badges = self.get_all()
        unlocked = [b for b in all_badges if b['unlocked']]

        by_rarity = {}
        for rarity in ['common', 'rare', 'epic', 'legendary']:
            total = len([b for b in all_badges if b['rarity'] == rarity])
            have = len([b for b in unlocked if b['rarity'] == rarity])
            by_rarity[rarity] = {'total': total, 'have': have}

        return {
            'total': len(all_badges),
            'unlocked': len(unlocked),
            'percentage': (len(unlocked) / len(all_badges)) * 100 if all_badges else 0,
            'by_rarity': by_rarity,
        }


def check_badge_unlock(state, condition_type, value):
    """Helper para verificar y desbloquear badges."""
    manager = BadgeManager(state)
    return manager.check_and_unlock(condition_type, value)


def get_all_badges():
    """Obtiene la definición de todos los badges."""
    return list(BADGES.values())
