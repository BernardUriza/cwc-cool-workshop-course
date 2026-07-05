# PromptCraft - Achievement Tracker
# Seguimiento de logros y estadísticas

from browser import window


class AchievementTracker:
    """
    Rastrea logros y estadísticas del usuario.
    """

    def __init__(self, state):
        self.state = state

    def track_lesson_complete(self, lesson_id, time_spent=0):
        """
        Registra la completación de una lección.

        Args:
            lesson_id: ID de la lección
            time_spent: Tiempo en segundos
        """
        if 'lessons_completed' not in self.state.data:
            self.state.data['lessons_completed'] = []

        if lesson_id not in self.state.data['lessons_completed']:
            self.state.data['lessons_completed'].append(lesson_id)

        # Estadísticas
        self._update_stats('lessons', {
            'total_completed': len(self.state.data['lessons_completed']),
            'total_time': self._get_stat('lessons', 'total_time', 0) + time_spent,
        })

        self.state.save()

        # Verificar badges
        from .badges import check_badge_unlock
        count = len(self.state.data['lessons_completed'])
        check_badge_unlock(self.state, 'lessons_completed', count)

        # Verificar badge de lección específica
        check_badge_unlock(self.state, 'lesson_complete', lesson_id)

    def track_puzzle_complete(self, puzzle_id, result):
        """
        Registra la completación de un puzzle.

        Args:
            puzzle_id: ID del puzzle
            result: Dict con time, stars, hints_used
        """
        if 'puzzles_completed' not in self.state.data:
            self.state.data['puzzles_completed'] = {}

        # Guardar/actualizar mejor resultado
        existing = self.state.data['puzzles_completed'].get(puzzle_id, {})

        if not existing or result.get('stars', 0) > existing.get('best_stars', 0):
            existing['best_stars'] = result.get('stars', 0)

        if not existing.get('best_time') or result.get('time', 999999) < existing.get('best_time', 999999):
            existing['best_time'] = result.get('time')

        existing['solved'] = True
        existing['attempts'] = existing.get('attempts', 0) + 1
        existing['last_solved'] = str(window.Date.new())

        self.state.data['puzzles_completed'][puzzle_id] = existing

        # Estadísticas
        self._update_stats('puzzles', {
            'total_solved': len(self.state.data['puzzles_completed']),
            'total_3_stars': len([p for p in self.state.data['puzzles_completed'].values()
                                 if p.get('best_stars', 0) == 3]),
        })

        self.state.save()

        # Verificar badges
        from .badges import check_badge_unlock
        count = len(self.state.data['puzzles_completed'])
        check_badge_unlock(self.state, 'puzzles_solved', count)

        if result.get('stars') == 3:
            check_badge_unlock(self.state, 'puzzle_stars', 3)

        if result.get('hints_used', 1) == 0:
            check_badge_unlock(self.state, 'puzzle_no_hints', True)

        if result.get('time', 999) < 120:
            check_badge_unlock(self.state, 'puzzle_time', result['time'])

    def track_playground_use(self):
        """Registra uso del playground."""
        count = self._get_stat('playground', 'uses', 0) + 1
        self._update_stats('playground', {'uses': count})
        self.state.save()

        from .badges import check_badge_unlock
        check_badge_unlock(self.state, 'playground_use', count)

    def track_daily_login(self):
        """Registra login diario."""
        today = self._get_today()
        last_login = self.state.data.get('last_login')

        if last_login != today:
            self.state.data['last_login'] = today

            # Verificar hora para badges especiales
            hour = window.Date.new().getHours()

            from .badges import check_badge_unlock
            if hour < 7:
                check_badge_unlock(self.state, 'time_of_day', 'early')
            elif hour >= 0 and hour < 5:
                check_badge_unlock(self.state, 'time_of_day', 'night')

            self.state.save()

    def _get_today(self):
        """Obtiene fecha de hoy."""
        now = window.Date.new()
        return f"{now.getFullYear()}-{str(now.getMonth() + 1).zfill(2)}-{str(now.getDate()).zfill(2)}"

    def _update_stats(self, category, stats):
        """Actualiza estadísticas."""
        if 'stats' not in self.state.data:
            self.state.data['stats'] = {}
        if category not in self.state.data['stats']:
            self.state.data['stats'][category] = {}

        self.state.data['stats'][category].update(stats)

    def _get_stat(self, category, key, default=None):
        """Obtiene una estadística."""
        return self.state.data.get('stats', {}).get(category, {}).get(key, default)

    def get_all_stats(self):
        """Obtiene todas las estadísticas."""
        stats = self.state.data.get('stats', {})

        return {
            'lessons': {
                'completed': len(self.state.data.get('lessons_completed', [])),
                'total_time': stats.get('lessons', {}).get('total_time', 0),
            },
            'puzzles': {
                'solved': len(self.state.data.get('puzzles_completed', {})),
                'three_stars': len([p for p in self.state.data.get('puzzles_completed', {}).values()
                                   if p.get('best_stars', 0) == 3]),
            },
            'xp': {
                'total': self.state.data.get('xp', 0),
            },
            'streak': {
                'current': self.state.data.get('streak', {}).get('current', 0),
                'max': self.state.data.get('streak', {}).get('max', 0),
            },
            'badges': {
                'unlocked': len(self.state.data.get('badges', [])),
            },
            'playground': {
                'uses': stats.get('playground', {}).get('uses', 0),
            },
        }

    def get_progress_summary(self):
        """Obtiene resumen de progreso general."""
        stats = self.get_all_stats()

        # Calcular porcentaje de completación
        total_lessons = 20  # Número total de lecciones
        total_puzzles = 15  # Número total de puzzles
        total_badges = 30   # Número total de badges

        lesson_progress = (stats['lessons']['completed'] / total_lessons) * 100
        puzzle_progress = (stats['puzzles']['solved'] / total_puzzles) * 100
        badge_progress = (stats['badges']['unlocked'] / total_badges) * 100

        overall = (lesson_progress + puzzle_progress + badge_progress) / 3

        return {
            'overall': round(overall, 1),
            'lessons': round(lesson_progress, 1),
            'puzzles': round(puzzle_progress, 1),
            'badges': round(badge_progress, 1),
            'stats': stats,
        }


def check_achievements(state, event_type, event_data=None):
    """
    Verifica logros después de un evento.

    Args:
        state: Estado de la aplicación
        event_type: Tipo de evento
        event_data: Datos del evento
    """
    tracker = AchievementTracker(state)

    if event_type == 'lesson_complete':
        tracker.track_lesson_complete(
            event_data.get('lesson_id'),
            event_data.get('time_spent', 0)
        )
    elif event_type == 'puzzle_complete':
        tracker.track_puzzle_complete(
            event_data.get('puzzle_id'),
            event_data
        )
    elif event_type == 'playground_use':
        tracker.track_playground_use()
    elif event_type == 'daily_login':
        tracker.track_daily_login()
