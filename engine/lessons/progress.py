# PromptCraft - Lesson Progress
# Seguimiento del progreso de lecciones

from browser import timer
from ..state import get_state
from ..gamification.xp import XPManager
from ..gamification.badges import BadgeManager
from ..gamification.achievements import check_achievements


class LessonProgress:
    """Gestiona el progreso de lecciones del usuario."""

    def __init__(self, state=None):
        """
        Inicializa el tracker de progreso.

        Args:
            state: Estado de la aplicación (opcional)
        """
        self.state = state or get_state()

    def get_lesson_status(self, lesson_id):
        """
        Obtiene el estado de una lección.

        Args:
            lesson_id: ID de la lección

        Returns:
            dict con estado de la lección
        """
        completed = self.state.data.get('completed_lessons', [])
        in_progress = self.state.data.get('lessons_in_progress', {})

        if lesson_id in completed:
            return {
                'status': 'completed',
                'completed': True,
                'in_progress': False,
                'progress': 100
            }
        elif lesson_id in in_progress:
            progress_data = in_progress[lesson_id]
            return {
                'status': 'in_progress',
                'completed': False,
                'in_progress': True,
                'progress': progress_data.get('progress', 0),
                'current_section': progress_data.get('current_section', 0),
                'started_at': progress_data.get('started_at')
            }
        else:
            return {
                'status': 'not_started',
                'completed': False,
                'in_progress': False,
                'progress': 0
            }

    def start_lesson(self, lesson_id):
        """
        Marca una lección como iniciada.

        Args:
            lesson_id: ID de la lección

        Returns:
            dict con estado actualizado
        """
        if lesson_id in self.state.data.get('completed_lessons', []):
            return self.get_lesson_status(lesson_id)

        in_progress = self.state.data.get('lessons_in_progress', {})

        if lesson_id not in in_progress:
            from datetime import datetime
            in_progress[lesson_id] = {
                'started_at': datetime.now().isoformat(),
                'current_section': 0,
                'progress': 0
            }
            self.state.data['lessons_in_progress'] = in_progress
            self.state.save()

        return self.get_lesson_status(lesson_id)

    def update_progress(self, lesson_id, section_index, total_sections):
        """
        Actualiza el progreso de una lección.

        Args:
            lesson_id: ID de la lección
            section_index: Índice de la sección actual
            total_sections: Total de secciones

        Returns:
            dict con progreso actualizado
        """
        if lesson_id in self.state.data.get('completed_lessons', []):
            return self.get_lesson_status(lesson_id)

        in_progress = self.state.data.get('lessons_in_progress', {})

        if lesson_id not in in_progress:
            self.start_lesson(lesson_id)
            in_progress = self.state.data.get('lessons_in_progress', {})

        progress = int((section_index + 1) / total_sections * 100)

        in_progress[lesson_id] = {
            **in_progress.get(lesson_id, {}),
            'current_section': section_index,
            'progress': progress
        }

        self.state.data['lessons_in_progress'] = in_progress
        self.state.save()

        return self.get_lesson_status(lesson_id)

    def complete_lesson(self, lesson_id, lesson_data):
        """
        Marca una lección como completada y otorga XP.

        Args:
            lesson_id: ID de la lección
            lesson_data: dict con datos de la lección

        Returns:
            dict con resultados de la compleción
        """
        completed = self.state.data.get('completed_lessons', [])

        # Verificar si ya estaba completada
        already_completed = lesson_id in completed

        if not already_completed:
            # Marcar como completada
            completed.append(lesson_id)
            self.state.data['completed_lessons'] = completed

            # Remover de en progreso
            in_progress = self.state.data.get('lessons_in_progress', {})
            if lesson_id in in_progress:
                del in_progress[lesson_id]
                self.state.data['lessons_in_progress'] = in_progress

            # Otorgar XP
            xp_mgr = XPManager(self.state)
            xp_reward = lesson_data.get('xp_reward', 50)
            xp_result = xp_mgr.add_xp(xp_reward, 'lesson_complete')

            # Verificar badges
            badge_mgr = BadgeManager(self.state)
            new_badges = badge_mgr.check_and_award('lesson_complete', {
                'lesson_id': lesson_id,
                'category': lesson_data.get('category'),
                'difficulty': lesson_data.get('difficulty'),
                'total_completed': len(completed)
            })

            # Verificar achievements
            check_achievements(self.state, 'lesson_complete', {
                'lesson_id': lesson_id,
                'lesson_data': lesson_data
            })

            self.state.save()

            return {
                'success': True,
                'first_time': True,
                'xp_earned': xp_reward,
                'xp_result': xp_result,
                'new_badges': new_badges,
                'total_completed': len(completed)
            }
        else:
            return {
                'success': True,
                'first_time': False,
                'xp_earned': 0,
                'total_completed': len(completed)
            }

    def complete_exercise(self, lesson_id, exercise_data, answer):
        """
        Registra la compleción de un ejercicio.

        Args:
            lesson_id: ID de la lección
            exercise_data: dict con datos del ejercicio
            answer: Respuesta del usuario

        Returns:
            dict con resultado
        """
        exercises = self.state.data.get('completed_exercises', {})

        if lesson_id not in exercises:
            exercises[lesson_id] = {
                'completed': True,
                'answer': answer[:500]  # Limitar longitud
            }
            self.state.data['completed_exercises'] = exercises
            self.state.save()

            # XP por ejercicio
            xp_mgr = XPManager(self.state)
            xp_mgr.add_xp(15, 'exercise_complete')

            return {
                'success': True,
                'first_time': True,
                'xp_earned': 15
            }
        else:
            return {
                'success': True,
                'first_time': False,
                'xp_earned': 0
            }

    def get_completed_count(self):
        """
        Obtiene cantidad de lecciones completadas.

        Returns:
            int con cantidad
        """
        return len(self.state.data.get('completed_lessons', []))

    def get_completed_lessons(self):
        """
        Obtiene lista de IDs de lecciones completadas.

        Returns:
            list de IDs
        """
        return self.state.data.get('completed_lessons', [])

    def get_in_progress_lessons(self):
        """
        Obtiene lecciones en progreso.

        Returns:
            dict con lecciones en progreso
        """
        return self.state.data.get('lessons_in_progress', {})

    def get_category_progress(self, category_id, total_in_category):
        """
        Obtiene progreso en una categoría.

        Args:
            category_id: ID de la categoría
            total_in_category: Total de lecciones en la categoría

        Returns:
            dict con progreso
        """
        from .loader import get_lessons_by_category

        lessons = get_lessons_by_category(category_id)
        completed = self.state.data.get('completed_lessons', [])

        completed_in_category = sum(
            1 for lesson in lessons
            if lesson['id'] in completed
        )

        return {
            'completed': completed_in_category,
            'total': total_in_category,
            'percentage': (completed_in_category / total_in_category * 100) if total_in_category > 0 else 0
        }

    def get_overall_progress(self, total_lessons):
        """
        Obtiene progreso general.

        Args:
            total_lessons: Total de lecciones

        Returns:
            dict con progreso
        """
        completed = len(self.state.data.get('completed_lessons', []))

        return {
            'completed': completed,
            'total': total_lessons,
            'percentage': (completed / total_lessons * 100) if total_lessons > 0 else 0
        }

    def get_next_lesson(self, lesson_id):
        """
        Obtiene la siguiente lección recomendada.

        Args:
            lesson_id: ID de la lección actual

        Returns:
            ID de la siguiente lección o None
        """
        from .loader import get_lesson

        current = get_lesson(lesson_id)
        if current and current.get('next_lesson'):
            return current['next_lesson']
        return None

    def reset_lesson(self, lesson_id):
        """
        Reinicia el progreso de una lección.

        Args:
            lesson_id: ID de la lección
        """
        # Remover de completadas
        completed = self.state.data.get('completed_lessons', [])
        if lesson_id in completed:
            completed.remove(lesson_id)
            self.state.data['completed_lessons'] = completed

        # Remover de en progreso
        in_progress = self.state.data.get('lessons_in_progress', {})
        if lesson_id in in_progress:
            del in_progress[lesson_id]
            self.state.data['lessons_in_progress'] = in_progress

        # Remover ejercicio
        exercises = self.state.data.get('completed_exercises', {})
        if lesson_id in exercises:
            del exercises[lesson_id]
            self.state.data['completed_exercises'] = exercises

        self.state.save()

    def get_stats(self):
        """
        Obtiene estadísticas generales de lecciones.

        Returns:
            dict con estadísticas
        """
        from .loader import get_all_lessons, get_categories

        all_lessons = get_all_lessons()
        completed = self.state.data.get('completed_lessons', [])
        in_progress = self.state.data.get('lessons_in_progress', {})

        # Por dificultad
        by_difficulty = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        for lesson in all_lessons:
            if lesson['id'] in completed:
                diff = lesson.get('difficulty', 'beginner')
                by_difficulty[diff] = by_difficulty.get(diff, 0) + 1

        # Por categoría
        categories = get_categories()
        by_category = {}
        for cat in categories:
            cat_lessons = [l for l in all_lessons if l.get('category') == cat['id']]
            completed_in_cat = [l for l in cat_lessons if l['id'] in completed]
            by_category[cat['id']] = {
                'total': len(cat_lessons),
                'completed': len(completed_in_cat),
                'percentage': (len(completed_in_cat) / len(cat_lessons) * 100) if cat_lessons else 0
            }

        # XP ganado en lecciones
        xp_from_lessons = sum(
            lesson.get('xp_reward', 0)
            for lesson in all_lessons
            if lesson['id'] in completed
        )

        return {
            'total': len(all_lessons),
            'completed': len(completed),
            'in_progress': len(in_progress),
            'not_started': len(all_lessons) - len(completed) - len(in_progress),
            'percentage': (len(completed) / len(all_lessons) * 100) if all_lessons else 0,
            'by_difficulty': by_difficulty,
            'by_category': by_category,
            'xp_earned': xp_from_lessons
        }


# Instancia global
_progress_tracker = None


def get_progress_tracker():
    """Obtiene el tracker de progreso."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = LessonProgress()
    return _progress_tracker


def get_lesson_progress(lesson_id):
    """Atajo para obtener progreso de una lección."""
    return get_progress_tracker().get_lesson_status(lesson_id)


def complete_lesson(lesson_id, lesson_data):
    """Atajo para completar una lección."""
    return get_progress_tracker().complete_lesson(lesson_id, lesson_data)
