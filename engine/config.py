# CWC - Course configuration loader
# El branding, los módulos activos y los textos del curso viven en
# content/course.json — el engine no se edita para cambiar de curso.

import json
from browser import window

_config = None

DEFAULTS = {
    'id': 'course',
    'name': 'CWC Workshop',
    'logo': '🎓',
    'tagline': 'Curso interactivo',
    'description': '',
    'language': 'es',
    'footer': 'Construido con cwc-cool-workshop-course',
    'features': {
        'lessons': True,
        'practice': True,
        'assessment': True,
        'puzzles': True,
        'playground': True,
        'retrieval': True,
        'final_project': True
    },
    'theme': {
        'primary': 'indigo'
    }
}


def http_get_json(url):
    req = window.XMLHttpRequest.new()
    req.open('GET', url, False)
    req.send()
    if req.status == 200:
        return json.loads(req.responseText)
    return None


def get_config():
    global _config
    if _config is None:
        data = http_get_json('content/course.json') or {}
        merged = dict(DEFAULTS)
        merged.update(data)
        features = dict(DEFAULTS['features'])
        features.update(data.get('features', {}))
        merged['features'] = features
        _config = merged
    return _config


def feature_enabled(name):
    return get_config()['features'].get(name, False)
