# PromptCraft - Streak System
# Sistema de rachas diarias

from browser import window


class StreakManager:
    """
    Gestiona las rachas de práctica diaria.
    """

    def __init__(self, state):
        self.state = state

    def get_info(self):
        """
        Obtiene información de la racha actual.

        Returns:
            Dict con info de la racha
        """
        streak_data = self.state.data.get('streak', {
            'current': 0,
            'max': 0,
            'last_date': None,
            'freezes': 0,
        })

        return {
            'current': streak_data.get('current', 0),
            'max': streak_data.get('max', 0),
            'last_date': streak_data.get('last_date'),
            'freezes': streak_data.get('freezes', 0),
            'is_active_today': self._is_active_today(),
        }

    def _is_active_today(self):
        """Verifica si ya practicó hoy."""
        last_date = self.state.data.get('streak', {}).get('last_date')
        if not last_date:
            return False

        today = self._get_today_string()
        return last_date == today

    def _get_today_string(self):
        """Obtiene la fecha de hoy como string."""
        now = window.Date.new()
        year = now.getFullYear()
        month = str(now.getMonth() + 1).zfill(2)
        day = str(now.getDate()).zfill(2)
        return f"{year}-{month}-{day}"

    def _get_yesterday_string(self):
        """Obtiene la fecha de ayer como string."""
        now = window.Date.new()
        yesterday = window.Date.new(now.getTime() - (24 * 60 * 60 * 1000))
        year = yesterday.getFullYear()
        month = str(yesterday.getMonth() + 1).zfill(2)
        day = str(yesterday.getDate()).zfill(2)
        return f"{year}-{month}-{day}"

    def update(self):
        """
        Actualiza la racha del usuario.
        Debe llamarse cuando el usuario practica.

        Returns:
            Dict con el resultado de la actualización
        """
        if 'streak' not in self.state.data:
            self.state.data['streak'] = {
                'current': 0,
                'max': 0,
                'last_date': None,
                'freezes': 0,
            }

        streak = self.state.data['streak']
        today = self._get_today_string()
        yesterday = self._get_yesterday_string()
        last_date = streak.get('last_date')

        result = {
            'previous': streak['current'],
            'new': streak['current'],
            'streak_broken': False,
            'streak_extended': False,
            'is_new_max': False,
        }

        if last_date == today:
            # Ya practicó hoy
            return result

        if last_date == yesterday:
            # Continuó la racha
            streak['current'] += 1
            result['streak_extended'] = True
        elif last_date is None:
            # Primera vez
            streak['current'] = 1
            result['streak_extended'] = True
        else:
            # Perdió la racha
            # Verificar si tiene freeze disponible
            if streak.get('freezes', 0) > 0:
                streak['freezes'] -= 1
                streak['current'] += 1
                result['streak_extended'] = True
                result['freeze_used'] = True
            else:
                result['streak_broken'] = True
                result['previous'] = streak['current']
                streak['current'] = 1

        streak['last_date'] = today

        # Verificar nuevo máximo
        if streak['current'] > streak.get('max', 0):
            streak['max'] = streak['current']
            result['is_new_max'] = True

        result['new'] = streak['current']

        self.state.data['streak'] = streak
        self.state.save()

        # Verificar badges de racha
        from .badges import check_badge_unlock
        check_badge_unlock(self.state, 'streak', streak['current'])

        return result

    def add_freeze(self, count=1):
        """
        Añade freezes de racha.

        Args:
            count: Número de freezes a añadir
        """
        if 'streak' not in self.state.data:
            self.state.data['streak'] = {'current': 0, 'max': 0, 'freezes': 0}

        self.state.data['streak']['freezes'] = \
            self.state.data['streak'].get('freezes', 0) + count

        self.state.save()

    def use_freeze(self):
        """
        Usa un freeze manualmente.

        Returns:
            True si se usó, False si no hay disponibles
        """
        freezes = self.state.data.get('streak', {}).get('freezes', 0)
        if freezes <= 0:
            return False

        self.state.data['streak']['freezes'] = freezes - 1
        self.state.save()
        return True

    def get_calendar(self, days=30):
        """
        Obtiene un calendario de actividad.

        Args:
            days: Número de días hacia atrás

        Returns:
            Lista de dicts con fecha y si hubo actividad
        """
        history = self.state.data.get('activity_history', [])
        history_set = set(history)

        calendar = []
        now = window.Date.new()

        for i in range(days - 1, -1, -1):
            date = window.Date.new(now.getTime() - (i * 24 * 60 * 60 * 1000))
            date_str = f"{date.getFullYear()}-{str(date.getMonth() + 1).zfill(2)}-{str(date.getDate()).zfill(2)}"

            calendar.append({
                'date': date_str,
                'day': date.getDate(),
                'active': date_str in history_set,
                'is_today': i == 0,
            })

        return calendar

    def record_activity(self):
        """Registra actividad para el calendario."""
        today = self._get_today_string()

        if 'activity_history' not in self.state.data:
            self.state.data['activity_history'] = []

        if today not in self.state.data['activity_history']:
            self.state.data['activity_history'].append(today)

            # Mantener solo últimos 365 días
            if len(self.state.data['activity_history']) > 365:
                self.state.data['activity_history'] = \
                    self.state.data['activity_history'][-365:]

            self.state.save()


def update_streak(state):
    """Helper para actualizar racha."""
    manager = StreakManager(state)
    return manager.update()


def get_streak_info(state):
    """Helper para obtener info de racha."""
    manager = StreakManager(state)
    return manager.get_info()
