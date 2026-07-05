# PromptCraft - XP System
# Sistema de experiencia

from ..components.toast import xp_toast


class XPManager:
    """
    Gestiona la experiencia del usuario.
    """

    # Multiplicadores de XP
    MULTIPLIERS = {
        'streak_bonus': 0.1,      # +10% por día de racha
        'perfect_bonus': 0.5,     # +50% por solución perfecta
        'speed_bonus': 0.25,      # +25% por terminar rápido
        'no_hints_bonus': 0.2,    # +20% por no usar pistas
    }

    # XP base por actividad
    BASE_XP = {
        'lesson_complete': 50,
        'puzzle_solve': 75,
        'playground_use': 10,
        'daily_login': 15,
        'streak_milestone': 100,  # Cada 7 días
        'level_up': 50,
        'badge_unlock': 25,
    }

    def __init__(self, state):
        """
        Args:
            state: Referencia al estado de la aplicación
        """
        self.state = state

    def award(self, activity, base_amount=None, modifiers=None, reason=''):
        """
        Otorga XP al usuario.

        Args:
            activity: Tipo de actividad
            base_amount: Cantidad base (o usa default)
            modifiers: Dict de modificadores a aplicar
            reason: Razón para mostrar en toast

        Returns:
            Dict con detalles del XP otorgado
        """
        # Determinar XP base
        if base_amount is None:
            base_amount = self.BASE_XP.get(activity, 10)

        modifiers = modifiers or {}
        total_multiplier = 1.0

        # Aplicar modificadores
        details = {'base': base_amount}

        for mod_name, mod_value in modifiers.items():
            if mod_value and mod_name in self.MULTIPLIERS:
                multiplier = self.MULTIPLIERS[mod_name]
                total_multiplier += multiplier
                details[mod_name] = int(base_amount * multiplier)

        # Bonus por racha
        streak = self.state.data.get('streak', {}).get('current', 0)
        if streak > 1:
            streak_mult = min(streak * self.MULTIPLIERS['streak_bonus'], 1.0)  # Max 100%
            total_multiplier += streak_mult
            details['streak'] = int(base_amount * streak_mult)

        # Calcular total
        total = int(base_amount * total_multiplier)
        details['total'] = total
        details['multiplier'] = total_multiplier

        # Añadir al estado
        old_xp = self.state.data.get('xp', 0)
        new_xp = old_xp + total
        old_level = self.state.get_level_info()['level']

        self.state.data['xp'] = new_xp
        self.state.save()

        # Verificar level up
        new_level = self.state.get_level_info()['level']
        if new_level > old_level:
            self._on_level_up(old_level, new_level)

        # Mostrar toast
        display_reason = reason or activity.replace('_', ' ').title()
        xp_toast(total, display_reason)

        # Registrar en historial
        self._log_xp_event(activity, total, details)

        return details

    def _on_level_up(self, old_level, new_level):
        """Callback cuando el usuario sube de nivel."""
        from ..components.modal import SuccessModal
        from .levels import get_level_title

        title = get_level_title(new_level)

        # Mostrar modal de nivel
        modal = SuccessModal(
            title='¡Subiste de Nivel!',
            message=f'¡Felicidades! Ahora eres nivel {new_level}: {title}',
            xp_gained=self.BASE_XP['level_up']
        )
        modal.show()

        # XP bonus por subir de nivel
        self.state.data['xp'] = self.state.data.get('xp', 0) + self.BASE_XP['level_up']
        self.state.save()

    def _log_xp_event(self, activity, amount, details):
        """Registra evento de XP en el historial."""
        from browser import window

        if 'xp_history' not in self.state.data:
            self.state.data['xp_history'] = []

        event = {
            'activity': activity,
            'amount': amount,
            'details': details,
            'timestamp': str(window.Date.new()),
        }

        # Mantener solo los últimos 100 eventos
        history = self.state.data['xp_history']
        history.append(event)
        if len(history) > 100:
            self.state.data['xp_history'] = history[-100:]

        self.state.save()

    def get_history(self, limit=20):
        """Obtiene historial de XP."""
        history = self.state.data.get('xp_history', [])
        return list(reversed(history[-limit:]))

    def get_stats(self):
        """Obtiene estadísticas de XP."""
        history = self.state.data.get('xp_history', [])

        total = self.state.data.get('xp', 0)
        today = 0
        this_week = 0

        from browser import window
        now = window.Date.new()
        today_start = window.Date.new(now.getFullYear(), now.getMonth(), now.getDate())
        week_start = window.Date.new(today_start.getTime() - (6 * 24 * 60 * 60 * 1000))

        for event in history:
            try:
                event_date = window.Date.new(event['timestamp'])
                if event_date >= today_start:
                    today += event['amount']
                if event_date >= week_start:
                    this_week += event['amount']
            except:
                pass

        return {
            'total': total,
            'today': today,
            'this_week': this_week,
            'average_daily': this_week // 7 if this_week > 0 else 0,
        }


def calculate_xp(activity, **modifiers):
    """
    Calcula XP para una actividad.

    Args:
        activity: Tipo de actividad
        **modifiers: Modificadores booleanos

    Returns:
        Cantidad de XP calculada
    """
    base = XPManager.BASE_XP.get(activity, 10)
    total_mult = 1.0

    for mod_name, active in modifiers.items():
        if active and mod_name in XPManager.MULTIPLIERS:
            total_mult += XPManager.MULTIPLIERS[mod_name]

    return int(base * total_mult)


def award_xp(state, activity, base_amount=None, modifiers=None, reason=''):
    """
    Helper para otorgar XP.

    Args:
        state: Estado de la aplicación
        activity: Tipo de actividad
        base_amount: Cantidad base
        modifiers: Dict de modificadores
        reason: Razón para mostrar

    Returns:
        Dict con detalles
    """
    manager = XPManager(state)
    return manager.award(activity, base_amount, modifiers, reason)
