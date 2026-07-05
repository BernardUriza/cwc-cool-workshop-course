# CWC - Retrieval sampler
# Muestreo espaciado 1+2+2 (retrievalpractice.org SpacingGuide):
# 1 pregunta de lo último cubierto, 2 de cobertura media, 2 de lo más viejo.
# Proxy de antigüedad: la posición de la lección en lessons_completed
# (el estado no guarda timestamps por lección).

import random
from ..config import http_get_json

QUIZ_SIZE = 5
RECENT_COUNT = 1
WEEK_COUNT = 2
MONTH_COUNT = 2

_bank = None


def get_bank():
    global _bank
    if _bank is None:
        _bank = http_get_json('content/quizzes.json') or {}
    return _bank


def sample_quiz(state):
    """Arma un quiz de 5 preguntas mezclando reciente / medio / viejo.

    Solo pregunta sobre lecciones YA completadas. Devuelve una lista de
    dicts pregunta (cada uno con su lesson_id anotado); vacía si el
    estudiante no ha completado nada o no hay banco.
    """
    bank = get_bank()
    completed = state.data.get('progress', {}).get('lessons_completed', [])
    covered = [lid for lid in completed if bank.get(lid)]
    if not covered:
        return []

    recent = covered[-1:]
    week = covered[-3:-1]
    month = covered[:-3]

    def key(q):
        return (q['lesson_id'], q['question'])

    picks = []
    seen = set()
    for lesson_ids, count in ((recent, RECENT_COUNT), (week, WEEK_COUNT), (month, MONTH_COUNT)):
        for q in _pick_from(bank, lesson_ids, count):
            if key(q) not in seen:
                seen.add(key(q))
                picks.append(q)

    if len(picks) < QUIZ_SIZE:
        backfill = [q for q in _pick_from(bank, covered, None) if key(q) not in seen]
        picks += backfill[:QUIZ_SIZE - len(picks)]

    random.shuffle(picks)
    return picks[:QUIZ_SIZE]


def _pick_from(bank, lesson_ids, count):
    pool = []
    for lid in lesson_ids:
        for q in bank.get(lid, []):
            question = dict(q)
            question['lesson_id'] = lid
            pool.append(question)
    random.shuffle(pool)
    return pool if count is None else pool[:count]
