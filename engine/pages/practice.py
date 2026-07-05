# Practice Sandbox - Práctica de Prompts con Evaluación
from browser import html, window, document
from ..state import get_state
from ..config import http_get_json

# Ejercicios de práctica con criterios de evaluación
PRACTICE_EXERCISES = http_get_json('content/practice.json') or []


def practice_page(params):
    """Renderiza la página de práctica."""
    state = get_state()
    container = html.DIV(Class="max-w-4xl mx-auto py-8 px-4")

    # Header
    header = html.DIV(Class="mb-8")
    header <= html.H1("✍️ Práctica", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P("Ejercicios con feedback instantáneo",
                     Class="text-gray-600")
    container <= header

    # Progreso
    practice_data = state.data.get('practice', {})
    completed = practice_data.get('completed_exercises', [])
    total = len(PRACTICE_EXERCISES)
    done = len(completed)

    progress_card = html.DIV(Class="bg-white rounded-xl shadow-sm p-4 mb-8 flex items-center justify-between")
    progress_left = html.DIV()
    progress_left <= html.SPAN(f"Progreso: {done}/{total} ejercicios", Class="font-medium text-gray-700")
    progress_card <= progress_left

    progress_bar = html.DIV(Class="w-48 bg-gray-200 rounded-full h-3")
    pct = (done / total * 100) if total > 0 else 0
    progress_bar <= html.DIV(
        Class="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full",
        style=f"width: {pct}%"
    )
    progress_card <= progress_bar
    container <= progress_card

    # Lista de ejercicios
    for exercise in PRACTICE_EXERCISES:
        is_completed = exercise['id'] in completed

        card = html.DIV(Class=f"bg-white rounded-xl shadow-sm p-6 mb-4 border-2 " +
                              ("border-green-300" if is_completed else "border-gray-100"))

        # Header del ejercicio
        card_header = html.DIV(Class="flex items-start justify-between mb-4")

        title_area = html.DIV()
        badge_colors = {
            'beginner': 'bg-green-100 text-green-800',
            'intermediate': 'bg-yellow-100 text-yellow-800',
            'advanced': 'bg-red-100 text-red-800'
        }
        badge = html.SPAN(
            exercise['difficulty'].capitalize(),
            Class=f"text-xs px-2 py-1 rounded-full font-medium {badge_colors.get(exercise['difficulty'], 'bg-gray-100')}"
        )
        title_area <= badge

        title_area <= html.H3(exercise['title'],
                              Class="text-lg font-semibold text-gray-800 mt-2")
        title_area <= html.P(exercise['scenario'], Class="text-gray-600 text-sm mt-1")

        card_header <= title_area

        if is_completed:
            card_header <= html.SPAN("✅", Class="text-2xl")

        card <= card_header

        # Botón
        btn_class = "px-4 py-2 rounded-lg font-medium " + (
            "bg-green-100 text-green-700" if is_completed else
            "bg-indigo-600 text-white hover:bg-indigo-700"
        )
        btn_text = "Repetir" if is_completed else "Practicar"

        btn = html.BUTTON(f"{btn_text} →", Class=btn_class)

        def make_handler(ex_id):
            def handler(ev):
                from ..router import get_router
                get_router().navigate(f'practice/{ex_id}')
            return handler

        btn.bind('click', make_handler(exercise['id']))
        card <= btn

        container <= card

    return container


def practice_exercise_page(params):
    """Renderiza un ejercicio individual de práctica."""
    state = get_state()
    exercise_id = params.get('id', '')

    # Buscar ejercicio
    exercise = None
    for ex in PRACTICE_EXERCISES:
        if ex['id'] == exercise_id:
            exercise = ex
            break

    if not exercise:
        container = html.DIV(Class="max-w-3xl mx-auto py-8 px-4")
        container <= html.H1("Ejercicio no encontrado", Class="text-2xl text-gray-800")
        return container

    container = html.DIV(Class="max-w-3xl mx-auto py-8 px-4")

    # Back button
    back_btn = html.A("← Volver a Práctica", href="#practice",
                      Class="text-indigo-600 hover:text-indigo-800 mb-4 inline-block")
    container <= back_btn

    # Header
    header = html.DIV(Class="mb-6")
    header <= html.H1(exercise['title'], Class="text-2xl font-bold text-gray-800 mb-2")

    cat_badge_colors = {
        'fundamentals': 'bg-blue-100 text-blue-800',
        'techniques': 'bg-green-100 text-green-800',
        'claude-code': 'bg-purple-100 text-purple-800',
        'project': 'bg-orange-100 text-orange-800'
    }
    header <= html.SPAN(exercise['category'].replace('-', ' ').title(),
                        Class=f"px-3 py-1 rounded-full text-sm {cat_badge_colors.get(exercise['category'], 'bg-gray-100')}")
    container <= header

    # Escenario
    scenario_card = html.DIV(Class="bg-indigo-50 border border-indigo-200 rounded-xl p-4 mb-6")
    scenario_card <= html.H3("📋 Escenario", Class="font-semibold text-indigo-800 mb-2")
    scenario_card <= html.P(exercise['scenario'], Class="text-indigo-700")
    container <= scenario_card

    # Tarea
    task_card = html.DIV(Class="bg-white border border-gray-200 rounded-xl p-4 mb-6")
    task_card <= html.H3("🎯 Tu tarea", Class="font-semibold text-gray-800 mb-2")
    task_card <= html.P(exercise['task'], Class="text-gray-700")
    container <= task_card

    # Editor de prompt
    editor_section = html.DIV(Class="mb-6")
    editor_section <= html.LABEL("✍️ Escribe tu prompt:", Class="block font-medium text-gray-700 mb-2")

    textarea = html.TEXTAREA(
        placeholder="Escribe tu prompt aquí...",
        Class="w-full h-48 p-4 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 resize-none font-mono",
        id=f"prompt-editor-{exercise_id}"
    )
    editor_section <= textarea

    # Contador de palabras
    word_count = html.DIV("0 palabras", Class="text-sm text-gray-500 mt-2", id="word-count")
    editor_section <= word_count

    container <= editor_section

    # Hints (collapsible)
    hints_section = html.DIV(Class="mb-6")
    hints_toggle = html.BUTTON("💡 Ver pistas", Class="text-indigo-600 hover:text-indigo-800 font-medium")
    hints_content = html.DIV(Class="hidden mt-3 bg-yellow-50 border border-yellow-200 rounded-xl p-4",
                             id="hints-content")
    hints_content <= html.UL(Class="list-disc list-inside space-y-1 text-yellow-800")
    for hint in exercise['hints']:
        hints_content.select('ul')[0] <= html.LI(hint)

    def toggle_hints(ev):
        content = document.getElementById("hints-content")
        if "hidden" in content.classList:
            content.classList.remove("hidden")
            ev.target.textContent = "💡 Ocultar pistas"
        else:
            content.classList.add("hidden")
            ev.target.textContent = "💡 Ver pistas"

    hints_toggle.bind('click', toggle_hints)
    hints_section <= hints_toggle
    hints_section <= hints_content
    container <= hints_section

    # Botón evaluar
    eval_btn = html.BUTTON(
        "🔍 Evaluar mi Prompt",
        Class="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 mb-6"
    )

    def evaluate(ev):
        textarea_el = document.getElementById(f"prompt-editor-{exercise_id}")
        user_prompt = textarea_el.value.strip()

        if len(user_prompt) < 10:
            _show_feedback(container, exercise, {}, "Escribe un prompt más largo para evaluar.", user_prompt)
            return

        results = _evaluate_prompt(user_prompt, exercise)
        _show_feedback(container, exercise, results, None, user_prompt)

    eval_btn.bind('click', evaluate)
    container <= eval_btn

    # Área de feedback (se llenará después de evaluar)
    feedback_area = html.DIV(id="feedback-area")
    container <= feedback_area

    # Actualizar contador de palabras
    def update_word_count(ev):
        text = ev.target.value
        words = len(text.split()) if text.strip() else 0
        document.getElementById("word-count").textContent = f"{words} palabras"

    textarea.bind('input', update_word_count)

    return container


def _evaluate_prompt(prompt, exercise):
    """Evalúa el prompt según los criterios del ejercicio."""
    prompt_lower = prompt.lower()
    words = prompt.split()
    word_count = len(words)
    results = {}

    for criterion in exercise['criteria']:
        check = criterion['check']
        passed = False

        # Verificaciones
        if check == 'verb':
            verbs = ['resume', 'extrae', 'lista', 'analiza', 'explica', 'describe',
                    'genera', 'crea', 'escribe', 'traduce', 'compara', 'evalúa', 'clasifica']
            passed = any(v in prompt_lower for v in verbs)

        elif check == 'number':
            import re
            passed = bool(re.search(r'\d+', prompt))

        elif check == 'format':
            format_words = ['lista', 'bullet', 'tabla', 'json', 'markdown', 'formato', 'puntos', 'numerado']
            passed = any(w in prompt_lower for w in format_words)

        elif check == 'audience':
            audience_words = ['niño', 'años', 'edad', 'principiante', 'experto', 'estudiante', 'profesional']
            passed = any(w in prompt_lower for w in audience_words)

        elif check == 'simple':
            simple_words = ['simple', 'sencillo', 'fácil', 'básico', 'claro', 'sin jerga', 'sin tecnicismos']
            passed = any(w in prompt_lower for w in simple_words)

        elif check == 'analogy':
            analogy_words = ['como', 'ejemplo', 'analogía', 'comparación', 'imagina', 'similar']
            passed = any(w in prompt_lower for w in analogy_words)

        elif check == 'examples':
            example_words = ['ejemplo', 'por ejemplo', 'e.g.', 'como:', 'entrada:', 'salida:', '→', '->']
            passed = sum(1 for w in example_words if w in prompt_lower) >= 2

        elif check == 'pattern':
            passed = ':' in prompt and ('\n' in prompt or '→' in prompt or '->' in prompt)

        elif check == 'categories':
            cat_words = ['positivo', 'negativo', 'neutro', 'categoría', 'clasifica como', 'tipo']
            passed = any(w in prompt_lower for w in cat_words)

        elif check == 'classify':
            passed = '?' in prompt or 'clasifica' in prompt_lower or 'sentimiento:' in prompt_lower

        elif check == 'step_by_step':
            step_words = ['paso a paso', 'paso por paso', 'step by step', 'primero', 'luego', 'finalmente', 'pasos']
            passed = any(w in prompt_lower for w in step_words)

        elif check == 'reasoning':
            reasoning_words = ['razonamiento', 'razona', 'explica por qué', 'justifica', 'muestra tu', 'pensemos']
            passed = any(w in prompt_lower for w in reasoning_words)

        elif check == 'conclusion':
            conclusion_words = ['conclusión', 'concluye', 'finalmente', 'respuesta final', 'por lo tanto']
            passed = any(w in prompt_lower for w in conclusion_words)

        elif check == 'role':
            role_words = ['actúa como', 'eres un', 'imagina que eres', 'como experto', 'en el rol de']
            passed = any(w in prompt_lower for w in role_words)

        elif check == 'expertise':
            expertise_words = ['experto', 'senior', 'profesional', 'especialista', 'desarrollador', 'años de experiencia']
            passed = any(w in prompt_lower for w in expertise_words)

        elif check == 'task':
            task_words = ['revisa', 'analiza', 'encuentra', 'identifica', 'busca', 'evalúa']
            passed = any(w in prompt_lower for w in task_words)

        elif check == 'aspects':
            passed = prompt.count('-') >= 2 or prompt.count('•') >= 2 or prompt.count('*') >= 2

        elif check == 'file':
            file_words = ['.py', '.js', '.ts', '.html', '.css', 'archivo', 'file', 'en el']
            passed = any(w in prompt_lower for w in file_words)

        elif check == 'function':
            func_words = ['función', 'function', 'método', 'method', 'def ', 'agregar', 'crear']
            passed = any(w in prompt_lower for w in func_words)

        elif check == 'requirements':
            passed = prompt.count('-') >= 2 or word_count >= 30

        elif check == 'style':
            style_words = ['estilo', 'existente', 'proyecto', 'consistente', 'sigue el']
            passed = any(w in prompt_lower for w in style_words)

        elif check == 'error':
            error_words = ['error', 'exception', 'typeerror', 'traceback', 'bug', 'falla']
            passed = any(w in prompt_lower for w in error_words)

        elif check == 'location':
            location_words = ['línea', 'archivo', 'line', 'file', '.py', '.js']
            passed = any(w in prompt_lower for w in location_words)

        elif check == 'expected':
            expected_words = ['debería', 'esperado', 'expected', 'quiero que', 'necesito que']
            passed = any(w in prompt_lower for w in expected_words)

        elif check == 'context':
            passed = word_count >= 20

        elif check == 'specific':
            passed = word_count >= 25

        elif check == 'technique':
            technique_words = ['paso a paso', 'actúa como', 'ejemplo', 'eres un']
            passed = any(w in prompt_lower for w in technique_words)

        elif check.startswith('min_words_'):
            min_words = int(check.split('_')[2])
            passed = word_count >= min_words

        results[criterion['id']] = passed

    return results


def _show_feedback(container, exercise, results, error_msg, user_prompt):
    """Muestra el feedback de la evaluación."""
    feedback_area = document.getElementById("feedback-area")
    feedback_area.innerHTML = ""

    if error_msg:
        feedback_area <= html.DIV(
            error_msg,
            Class="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-xl p-4 mb-4"
        )
        return

    # Calcular score
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    score = int((passed / total) * 100) if total > 0 else 0

    # Header de resultados
    result_card = html.DIV(Class="bg-white border border-gray-200 rounded-xl p-6 mb-4")

    score_color = "text-green-600" if score >= 80 else ("text-yellow-600" if score >= 60 else "text-red-600")
    result_card <= html.DIV(
        f"Puntuación: {score}%",
        Class=f"text-3xl font-bold {score_color} mb-4"
    )

    # Criterios
    criteria_list = html.DIV(Class="space-y-2")

    for criterion in exercise['criteria']:
        passed = results.get(criterion['id'], False)

        crit_item = html.DIV(Class="flex items-center gap-3 p-2 rounded-lg " +
                                   ("bg-green-50" if passed else "bg-red-50"))
        crit_item <= html.SPAN("✅" if passed else "❌", Class="text-lg")

        crit_text = html.DIV()
        crit_text <= html.SPAN(criterion['name'], Class="font-medium " +
                                                        ("text-green-800" if passed else "text-red-800"))
        crit_text <= html.P(criterion['description'], Class="text-sm " +
                                                             ("text-green-600" if passed else "text-red-600"))
        crit_item <= crit_text
        criteria_list <= crit_item

    result_card <= criteria_list
    feedback_area <= result_card

    # Si pasó el 80%, dar XP y marcar completado
    if score >= 80:
        state = get_state()
        practice_data = state.data.get('practice', {})
        completed = practice_data.get('completed_exercises', [])

        if exercise['id'] not in completed:
            completed.append(exercise['id'])
            practice_data['completed_exercises'] = completed
            state.data['practice'] = practice_data
            state.save()

            # Dar XP
            from ..gamification.xp import award_xp
            award_xp(state, 'practice', exercise['xp_reward'], None, f"Completar ejercicio: {exercise['title']}")

            success_msg = html.DIV(
                Class="bg-green-100 border border-green-300 rounded-xl p-4 mb-4 text-center"
            )
            success_msg <= html.P("🎉 ¡Excelente! Has completado este ejercicio.", Class="text-green-800 font-medium")
            success_msg <= html.P(f"+{exercise['xp_reward']} XP ganados", Class="text-green-600")
            feedback_area <= success_msg

    # Ver ejemplo
    if exercise.get('example_prompt') and exercise['example_prompt'] != 'No hay ejemplo - ¡este es TU prompt único!':
        example_section = html.DIV(Class="mt-6")
        example_toggle = html.BUTTON("📝 Ver ejemplo de prompt", Class="text-indigo-600 hover:text-indigo-800 font-medium")
        example_content = html.DIV(Class="hidden mt-3", id="example-content")

        example_box = html.DIV(Class="bg-gray-50 border border-gray-200 rounded-xl p-4")
        example_box <= html.H4("Ejemplo de buen prompt:", Class="font-semibold text-gray-700 mb-2")
        example_box <= html.PRE(exercise['example_prompt'], Class="whitespace-pre-wrap text-sm text-gray-600 font-mono")
        example_content <= example_box

        def toggle_example(ev):
            content = document.getElementById("example-content")
            if "hidden" in content.classList:
                content.classList.remove("hidden")
                ev.target.textContent = "📝 Ocultar ejemplo"
            else:
                content.classList.add("hidden")
                ev.target.textContent = "📝 Ver ejemplo de prompt"

        example_toggle.bind('click', toggle_example)
        example_section <= example_toggle
        example_section <= example_content
        feedback_area <= example_section
