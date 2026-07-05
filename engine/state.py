"""
PromptCraft - State Management
Sistema de estado global con persistencia en localStorage
"""
from browser import window, console
from browser.local_storage import storage
import json
from datetime import datetime


class AppState:
    """
    Estado global de la aplicación con persistencia en localStorage.

    Estructura del estado:
    {
        'user': {
            'id': str,
            'username': str,
            'created_at': str
        },
        'progress': {
            'xp': int,
            'level': int,
            'lessons_completed': [str],
            'puzzles_solved': {puzzle_id: {stars, time, hints_used}},
            'exercises_completed': [str]
        },
        'streak': {
            'current': int,
            'longest': int,
            'last_date': str,
            'freezes_available': int,
            'freezes_used': int
        },
        'badges': [str],
        'preferences': {
            'theme': 'light' | 'dark',
            'sound': bool,
            'notifications': bool
        },
        'stats': {
            'total_time_spent': int,
            'puzzles_attempted': int,
            'hints_used_total': int,
            'perfect_puzzles': int
        }
    }
    """

    STORAGE_KEY = 'promptcraft_state'

    # Level thresholds
    LEVEL_THRESHOLDS = [0, 100, 350, 850, 1600, 2600, 4100, 6100, 9100, 14100, 20000]

    # Level titles
    LEVEL_TITLES = [
        "Novato",           # 1
        "Aprendiz",         # 2
        "Estudiante",       # 3
        "Practicante",      # 4
        "Competente",       # 5
        "Hábil",            # 6
        "Experto",          # 7
        "Maestro",          # 8
        "Gurú",             # 9
        "Leyenda",          # 10
    ]

    def __init__(self):
        self._state = self._get_default_state()
        self._listeners = []
        self._badge_listeners = []
        self.load()

    @property
    def data(self):
        """Acceso al estado interno."""
        return self._state

    def get_level_info(self):
        """Obtiene información del nivel actual para el navbar y páginas."""
        xp_progress = self.get_xp_progress()
        return {
            'level': xp_progress['level'],
            'title': self.get_level_title(xp_progress['level']),
            'progress': xp_progress['progress_percent'],
            'xp': xp_progress['current_xp'],
            'xp_needed': xp_progress['xp_needed'],
            'xp_in_level': xp_progress['xp_in_level'],
            'xp_for_next': xp_progress['xp_for_next_level'],
            'xp_for_current': xp_progress['xp_for_current_level'],
        }

    def _get_default_state(self):
        """Estado por defecto para nuevos usuarios"""
        return {
            'user': {
                'id': self._generate_id(),
                'username': 'Usuario',
                'created_at': datetime.now().isoformat()
            },
            'progress': {
                'xp': 0,
                'level': 1,
                'lessons_completed': [],
                'puzzles_solved': {},
                'exercises_completed': []
            },
            'streak': {
                'current': 0,
                'longest': 0,
                'last_date': None,
                'freezes_available': 2,
                'freezes_used': 0
            },
            'badges': [],
            'preferences': {
                'theme': 'light',
                'sound': True,
                'notifications': True
            },
            'stats': {
                'total_time_spent': 0,
                'puzzles_attempted': 0,
                'hints_used_total': 0,
                'perfect_puzzles': 0
            }
        }

    def _generate_id(self):
        """Generar ID único para el usuario"""
        import random
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(12))

    def load(self):
        """Cargar estado desde localStorage"""
        try:
            saved = storage.get(self.STORAGE_KEY)
            if saved:
                loaded_state = json.loads(saved)
                # Merge con defaults para manejar nuevos campos
                self._state = self._merge_with_defaults(loaded_state)
                console.log(f"[State] Loaded: {self._state['progress']['xp']} XP, Level {self._state['progress']['level']}")
            else:
                console.log("[State] No saved state found, using defaults")
        except Exception as e:
            console.log(f"[State] Error loading: {e}")

    def _merge_with_defaults(self, loaded):
        """Merge estado cargado con defaults para manejar nuevos campos"""
        defaults = self._get_default_state()

        def deep_merge(base, override):
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(defaults, loaded)

    def save(self):
        """Guardar estado en localStorage"""
        try:
            storage[self.STORAGE_KEY] = json.dumps(self._state)
        except Exception as e:
            console.log(f"[State] Error saving: {e}")

    def get(self, key, default=None):
        """
        Obtener un valor del estado usando notación de punto.
        Ejemplo: state.get('progress.xp')
        """
        keys = key.split('.')
        value = self._state
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value, save=True):
        """
        Establecer un valor en el estado.
        Ejemplo: state.set('progress.xp', 100)
        """
        keys = key.split('.')
        target = self._state
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        old_value = target.get(keys[-1])
        target[keys[-1]] = value

        if save:
            self.save()

        self._notify_listeners(key, value, old_value)

    def subscribe(self, callback):
        """
        Suscribirse a cambios de estado.
        El callback recibe (key, new_value, old_value)
        """
        self._listeners.append(callback)
        return lambda: self._listeners.remove(callback)

    def subscribe_badges(self, callback):
        """Suscribirse específicamente a nuevos badges"""
        self._badge_listeners.append(callback)
        return lambda: self._badge_listeners.remove(callback)

    def _notify_listeners(self, key, new_value, old_value):
        """Notificar a los listeners sobre cambios"""
        for callback in self._listeners:
            try:
                callback(key, new_value, old_value)
            except Exception as e:
                console.log(f"[State] Listener error: {e}")

    def _notify_badge_listeners(self, badge_id):
        """Notificar sobre nuevo badge"""
        for callback in self._badge_listeners:
            try:
                callback(badge_id)
            except Exception as e:
                console.log(f"[State] Badge listener error: {e}")

    # =========================================================================
    # XP & LEVEL SYSTEM
    # =========================================================================

    def add_xp(self, amount, reason=""):
        """
        Agregar XP y verificar level up.

        Returns:
            dict: {
                'xp_gained': int,
                'total_xp': int,
                'level_up': bool,
                'new_level': int,
                'level_title': str
            }
        """
        current_xp = self.get('progress.xp', 0)
        current_level = self.get('progress.level', 1)

        new_xp = current_xp + amount
        new_level = self._calculate_level(new_xp)

        self.set('progress.xp', new_xp, save=False)

        result = {
            'xp_gained': amount,
            'total_xp': new_xp,
            'level_up': False,
            'new_level': new_level,
            'level_title': self.get_level_title(new_level),
            'reason': reason
        }

        if new_level > current_level:
            self.set('progress.level', new_level, save=False)
            result['level_up'] = True
            console.log(f"[State] Level up! {current_level} -> {new_level}")

        self.save()
        console.log(f"[State] +{amount} XP ({reason}). Total: {new_xp}")

        return result

    def _calculate_level(self, xp):
        """Calcular nivel basado en XP total"""
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if xp < threshold:
                return max(1, i)
        return 10

    def get_level_title(self, level=None):
        """Obtener título del nivel"""
        if level is None:
            level = self.get('progress.level', 1)
        index = min(level - 1, len(self.LEVEL_TITLES) - 1)
        return self.LEVEL_TITLES[index]

    def get_xp_progress(self):
        """
        Obtener progreso de XP hacia el siguiente nivel.

        Returns:
            dict: {
                'current_xp': int,
                'level': int,
                'xp_for_current_level': int,
                'xp_for_next_level': int,
                'xp_in_level': int,
                'xp_needed': int,
                'progress_percent': float
            }
        """
        current_xp = self.get('progress.xp', 0)
        level = self.get('progress.level', 1)

        if level >= 10:
            return {
                'current_xp': current_xp,
                'level': level,
                'xp_for_current_level': self.LEVEL_THRESHOLDS[-1],
                'xp_for_next_level': self.LEVEL_THRESHOLDS[-1],
                'xp_in_level': 0,
                'xp_needed': 0,
                'progress_percent': 100
            }

        xp_for_current = self.LEVEL_THRESHOLDS[level - 1] if level > 1 else 0
        xp_for_next = self.LEVEL_THRESHOLDS[level]
        xp_in_level = current_xp - xp_for_current
        xp_needed = xp_for_next - current_xp
        level_range = xp_for_next - xp_for_current
        progress = (xp_in_level / level_range) * 100 if level_range > 0 else 0

        return {
            'current_xp': current_xp,
            'level': level,
            'xp_for_current_level': xp_for_current,
            'xp_for_next_level': xp_for_next,
            'xp_in_level': xp_in_level,
            'xp_needed': xp_needed,
            'progress_percent': round(progress, 1)
        }

    # =========================================================================
    # STREAK SYSTEM
    # =========================================================================

    def update_streak(self):
        """
        Actualizar streak basado en la fecha actual.
        Debe llamarse cuando el usuario completa una actividad.

        Returns:
            dict: {
                'current': int,
                'increased': bool,
                'freeze_used': bool,
                'lost': bool
            }
        """
        today = datetime.now().strftime('%Y-%m-%d')
        last_date = self.get('streak.last_date')
        current = self.get('streak.current', 0)
        longest = self.get('streak.longest', 0)
        freezes = self.get('streak.freezes_available', 2)

        result = {
            'current': current,
            'increased': False,
            'freeze_used': False,
            'lost': False
        }

        if last_date == today:
            # Ya se registró actividad hoy
            return result

        if last_date is None:
            # Primera actividad
            new_streak = 1
            result['increased'] = True
        else:
            last = datetime.strptime(last_date, '%Y-%m-%d')
            today_dt = datetime.strptime(today, '%Y-%m-%d')
            diff_days = (today_dt - last).days

            if diff_days == 1:
                # Día consecutivo
                new_streak = current + 1
                result['increased'] = True
            elif diff_days == 2 and freezes > 0:
                # Usar freeze
                new_streak = current + 1
                self.set('streak.freezes_available', freezes - 1, save=False)
                self.set('streak.freezes_used', self.get('streak.freezes_used', 0) + 1, save=False)
                result['increased'] = True
                result['freeze_used'] = True
            else:
                # Streak perdido
                new_streak = 1
                result['lost'] = True if current > 0 else False

        result['current'] = new_streak
        self.set('streak.current', new_streak, save=False)
        self.set('streak.last_date', today, save=False)

        if new_streak > longest:
            self.set('streak.longest', new_streak, save=False)

        # Otorgar freeze cada 7 días
        if new_streak > 0 and new_streak % 7 == 0:
            current_freezes = self.get('streak.freezes_available', 0)
            if current_freezes < 2:
                self.set('streak.freezes_available', current_freezes + 1, save=False)

        self.save()
        return result

    # =========================================================================
    # PROGRESS TRACKING
    # =========================================================================

    def complete_lesson(self, lesson_id, xp_earned, quiz_score=None):
        """
        Marcar lección como completada.

        Returns:
            dict: Resultado de add_xp + info adicional
        """
        completed = self.get('progress.lessons_completed', [])

        if lesson_id in completed:
            return {'already_completed': True, 'xp_gained': 0}

        completed.append(lesson_id)
        self.set('progress.lessons_completed', completed, save=False)

        result = self.add_xp(xp_earned, f"Lección: {lesson_id}")
        result['already_completed'] = False
        result['lesson_id'] = lesson_id
        result['lessons_total'] = len(completed)

        # Actualizar streak
        streak_result = self.update_streak()
        result['streak'] = streak_result

        return result

    def solve_puzzle(self, puzzle_id, stars, time_seconds, hints_used, xp_earned):
        """
        Registrar puzzle resuelto.

        Returns:
            dict: Resultado de add_xp + info adicional
        """
        solved = self.get('progress.puzzles_solved', {})
        stats = self.get('stats', {})

        # Verificar si ya fue resuelto (solo contar mejor score)
        is_new = puzzle_id not in solved
        previous_stars = solved.get(puzzle_id, {}).get('stars', 0) if not is_new else 0

        # Solo actualizar si es nuevo o mejor
        if is_new or stars > previous_stars:
            solved[puzzle_id] = {
                'stars': stars,
                'time': time_seconds,
                'hints_used': hints_used,
                'solved_at': datetime.now().isoformat()
            }
            self.set('progress.puzzles_solved', solved, save=False)

        # Actualizar stats
        stats['puzzles_attempted'] = stats.get('puzzles_attempted', 0) + 1
        stats['hints_used_total'] = stats.get('hints_used_total', 0) + hints_used
        if stars == 3 and hints_used == 0:
            stats['perfect_puzzles'] = stats.get('perfect_puzzles', 0) + 1
        self.set('stats', stats, save=False)

        # Solo dar XP si es nuevo puzzle
        if is_new:
            result = self.add_xp(xp_earned, f"Puzzle: {puzzle_id}")
        else:
            result = {'xp_gained': 0, 'already_completed': True}
            self.save()

        result['puzzle_id'] = puzzle_id
        result['stars'] = stars
        result['is_new'] = is_new
        result['puzzles_total'] = len(solved)

        # Actualizar streak
        streak_result = self.update_streak()
        result['streak'] = streak_result

        return result

    def complete_exercise(self, exercise_id, xp_earned):
        """Marcar ejercicio como completado"""
        completed = self.get('progress.exercises_completed', [])

        if exercise_id in completed:
            return {'already_completed': True, 'xp_gained': 0}

        completed.append(exercise_id)
        self.set('progress.exercises_completed', completed, save=False)

        result = self.add_xp(xp_earned, f"Ejercicio: {exercise_id}")
        result['already_completed'] = False

        return result

    # =========================================================================
    # BADGES
    # =========================================================================

    def unlock_badge(self, badge_id):
        """
        Desbloquear un badge.

        Returns:
            bool: True si es nuevo, False si ya lo tenía
        """
        badges = self.get('badges', [])

        if badge_id in badges:
            return False

        badges.append(badge_id)
        self.set('badges', badges)

        console.log(f"[State] Badge unlocked: {badge_id}")
        self._notify_badge_listeners(badge_id)

        return True

    def has_badge(self, badge_id):
        """Verificar si tiene un badge"""
        return badge_id in self.get('badges', [])

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self):
        """Obtener estadísticas completas del usuario"""
        return {
            'xp': self.get('progress.xp', 0),
            'level': self.get('progress.level', 1),
            'level_title': self.get_level_title(),
            'lessons_completed': len(self.get('progress.lessons_completed', [])),
            'puzzles_solved': len(self.get('progress.puzzles_solved', {})),
            'exercises_completed': len(self.get('progress.exercises_completed', [])),
            'badges_earned': len(self.get('badges', [])),
            'current_streak': self.get('streak.current', 0),
            'longest_streak': self.get('streak.longest', 0),
            'perfect_puzzles': self.get('stats.perfect_puzzles', 0),
            'hints_used_total': self.get('stats.hints_used_total', 0),
            'xp_progress': self.get_xp_progress()
        }

    def get_puzzle_stats(self, puzzle_id):
        """Obtener stats de un puzzle específico"""
        solved = self.get('progress.puzzles_solved', {})
        return solved.get(puzzle_id, None)

    # =========================================================================
    # RESET & DEBUG
    # =========================================================================

    def reset(self):
        """Resetear todo el estado (para debug/testing)"""
        self._state = self._get_default_state()
        self.save()
        console.log("[State] State reset to defaults")

    def export_state(self):
        """Exportar estado como JSON string"""
        return json.dumps(self._state, indent=2)

    def import_state(self, json_string):
        """Importar estado desde JSON string"""
        try:
            self._state = json.loads(json_string)
            self.save()
            return True
        except:
            return False


# Singleton global
_state_instance = None

def get_state():
    """Obtener instancia singleton del estado"""
    global _state_instance
    if _state_instance is None:
        _state_instance = AppState()
    return _state_instance
