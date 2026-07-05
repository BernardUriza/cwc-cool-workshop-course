# CWC - Lesson Loader
# Las lecciones viven en content/lessons/ como JSON (una por archivo +
# index.json con categorías y orden). El engine solo las consume.

from ..config import http_get_json


class LessonLoader:

    def __init__(self):
        index = http_get_json('content/lessons/index.json') or {}
        self.categories = index.get('categories', [])
        self._lesson_ids = index.get('lessons', [])
        self._cache = {}

    def _fetch(self, lesson_id):
        if lesson_id not in self._cache:
            self._cache[lesson_id] = http_get_json(
                'content/lessons/' + lesson_id + '.json'
            )
        return self._cache[lesson_id]

    @property
    def lessons(self):
        result = {}
        for lid in self._lesson_ids:
            lesson = self._fetch(lid)
            if lesson:
                result[lid] = lesson
        return result

    def get_lesson(self, lesson_id):
        if lesson_id not in self._lesson_ids:
            return None
        return self._fetch(lesson_id)

    def get_all_lessons(self):
        return list(self.lessons.values())

    def get_lessons_by_category(self, category_id):
        return [
            l for l in self.get_all_lessons()
            if l.get('category') == category_id
        ]

    def get_categories(self):
        return sorted(self.categories, key=lambda c: c.get('order', 0))

    def get_category(self, category_id):
        for cat in self.categories:
            if cat['id'] == category_id:
                return cat
        return None

    def get_next_lesson(self, current_lesson_id):
        current = self.get_lesson(current_lesson_id)
        if current and current.get('next_lesson'):
            return self.get_lesson(current['next_lesson'])
        return None

    def get_previous_lesson(self, current_lesson_id):
        for lesson in self.get_all_lessons():
            if lesson.get('next_lesson') == current_lesson_id:
                return lesson
        return None

    def search_lessons(self, query):
        query = query.lower()
        results = []
        for lesson in self.get_all_lessons():
            searchable = ' '.join([
                lesson.get('title', ''),
                lesson.get('description', ''),
                ' '.join(lesson.get('objectives', []))
            ]).lower()
            if query in searchable:
                results.append(lesson)
        return results

    def get_lessons_by_difficulty(self, difficulty):
        return [
            lesson for lesson in self.get_all_lessons()
            if lesson.get('difficulty') == difficulty
        ]

    def get_total_xp_available(self):
        return sum(l.get('xp_reward', 0) for l in self.get_all_lessons())

    def get_total_duration(self):
        return sum(l.get('duration', 0) for l in self.get_all_lessons())

    def get_lesson_count(self):
        return len(self._lesson_ids)

    def get_category_stats(self, category_id):
        lessons = self.get_lessons_by_category(category_id)
        return {
            'count': len(lessons),
            'total_xp': sum(l.get('xp_reward', 0) for l in lessons),
            'total_duration': sum(l.get('duration', 0) for l in lessons),
            'difficulties': {
                'beginner': len([l for l in lessons if l.get('difficulty') == 'beginner']),
                'intermediate': len([l for l in lessons if l.get('difficulty') == 'intermediate']),
                'advanced': len([l for l in lessons if l.get('difficulty') == 'advanced'])
            }
        }


_loader = None


def get_loader():
    global _loader
    if _loader is None:
        _loader = LessonLoader()
    return _loader


def get_lesson(lesson_id):
    return get_loader().get_lesson(lesson_id)


def get_lessons_by_category(category_id):
    return get_loader().get_lessons_by_category(category_id)


def get_all_lessons():
    return get_loader().get_all_lessons()


def get_categories():
    return get_loader().get_categories()
