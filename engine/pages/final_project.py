# Final Project - Proyecto Final del Curso
from browser import html, document, window
from ..state import get_state

# Requisitos del proyecto final
PROJECT_REQUIREMENTS = [
    {
        'id': 'context',
        'name': 'Contexto',
        'description': 'Describe claramente la situación o problema a resolver',
        'icon': '📋'
    },
    {
        'id': 'technique',
        'name': 'Técnica aplicada',
        'description': 'Usa al menos una técnica aprendida (CoT, few-shot, role, etc)',
        'icon': '🎯'
    },
    {
        'id': 'specificity',
        'name': 'Especificidad',
        'description': 'El prompt es específico y detallado',
        'icon': '🔍'
    },
    {
        'id': 'format',
        'name': 'Formato',
        'description': 'Especifica el formato de salida deseado',
        'icon': '📝'
    },
    {
        'id': 'complete',
        'name': 'Completitud',
        'description': 'El prompt está completo y listo para usar',
        'icon': '✅'
    }
]


def final_project_page(params):
    """Renderiza la página del proyecto final."""
    state = get_state()
    project_data = state.data.get('final_project', {})
    container = html.DIV(Class="max-w-4xl mx-auto py-8 px-4")

    # Verificar si ya completó el proyecto
    if project_data.get('completed'):
        return _render_completed_project(container, project_data)

    # Header
    header = html.DIV(Class="text-center mb-8")
    header <= html.DIV("🎓", Class="text-6xl mb-4")
    header <= html.H1("Proyecto Final", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P("Demuestra todo lo que aprendiste creando tu prompt maestro",
                     Class="text-gray-600 text-lg")
    container <= header

    # Progreso del curso
    progress = _calculate_course_progress(state)

    if progress['percentage'] < 50:
        # No puede hacer el proyecto aún
        locked_card = html.DIV(Class="bg-yellow-50 border border-yellow-300 rounded-xl p-6 text-center")
        locked_card <= html.DIV("🔒", Class="text-4xl mb-4")
        locked_card <= html.H2("Proyecto Bloqueado", Class="text-xl font-bold text-yellow-800 mb-2")
        locked_card <= html.P(f"Completa al menos el 50% del curso para desbloquear el proyecto final.",
                              Class="text-yellow-700 mb-4")
        locked_card <= html.P(f"Tu progreso actual: {progress['percentage']}%", Class="text-yellow-600 font-medium")

        progress_bar = html.DIV(Class="w-full max-w-md mx-auto bg-yellow-200 rounded-full h-4 mt-4")
        progress_bar <= html.DIV(
            Class="bg-yellow-500 h-4 rounded-full transition-all",
            style=f"width: {progress['percentage']}%"
        )
        locked_card <= progress_bar
        container <= locked_card

        # Sugerencias
        suggestions = html.DIV(Class="mt-8")
        suggestions <= html.H3("📚 Continúa aprendiendo:", Class="font-semibold text-gray-800 mb-4")

        links = [
            ('#lessons', '📖 Lecciones', 'Aprende los conceptos'),
            ('#practice', '✍️ Práctica', 'Escribe tus propios prompts'),
            ('#claude-exercises', '🤖 Ejercicios Claude', 'Practica con Claude Code')
        ]

        for href, title, desc in links:
            link = html.A(
                href=href,
                Class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-indigo-300 mb-3"
            )
            link <= html.SPAN(title, Class="font-medium text-gray-800")
            link <= html.SPAN(f" - {desc}", Class="text-gray-500")
            suggestions <= link

        container <= suggestions
        return container

    # Instrucciones
    instructions = html.DIV(Class="bg-indigo-50 border border-indigo-200 rounded-xl p-6 mb-8")
    instructions <= html.H2("🎯 Tu Misión", Class="text-xl font-bold text-indigo-800 mb-4")

    mission_text = html.DIV(Class="text-indigo-700 space-y-2")
    mission_text <= html.P("Crea un prompt profesional para un caso REAL de tu vida:")
    mission_items = html.UL(Class="list-disc list-inside ml-4 space-y-1")
    mission_items <= html.LI("Puede ser para tu trabajo, estudios o hobby")
    mission_items <= html.LI("Debe usar las técnicas aprendidas en el curso")
    mission_items <= html.LI("Debe estar listo para usar con una IA real")
    mission_text <= mission_items
    instructions <= mission_text
    container <= instructions

    # Requisitos
    req_section = html.DIV(Class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8")
    req_section <= html.H3("📋 Requisitos del Proyecto", Class="font-bold text-gray-800 mb-4")

    req_grid = html.DIV(Class="grid grid-cols-1 md:grid-cols-2 gap-4")
    for req in PROJECT_REQUIREMENTS:
        req_card = html.DIV(Class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg")
        req_card <= html.SPAN(req['icon'], Class="text-xl")
        req_text = html.DIV()
        req_text <= html.P(req['name'], Class="font-medium text-gray-800")
        req_text <= html.P(req['description'], Class="text-sm text-gray-600")
        req_card <= req_text
        req_grid <= req_card

    req_section <= req_grid
    container <= req_section

    # Formulario del proyecto
    form_section = html.DIV(Class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8")

    # Campo: Título del proyecto
    form_section <= html.LABEL("📌 Título de tu proyecto", Class="block font-medium text-gray-700 mb-2")
    title_input = html.INPUT(
        type="text",
        placeholder="Ej: Prompt para analizar reportes de ventas",
        Class="w-full p-3 border border-gray-300 rounded-xl mb-6 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
        id="project-title"
    )
    # Cargar valor guardado
    if project_data.get('title'):
        title_input.value = project_data['title']
    form_section <= title_input

    # Campo: Contexto
    form_section <= html.LABEL("📋 Contexto / Situación", Class="block font-medium text-gray-700 mb-2")
    form_section <= html.P("¿Cuál es el problema que quieres resolver?", Class="text-sm text-gray-500 mb-2")
    context_input = html.TEXTAREA(
        placeholder="Describe la situación: quién eres, qué necesitas, para quién es...",
        Class="w-full h-24 p-3 border border-gray-300 rounded-xl mb-6 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
        id="project-context"
    )
    if project_data.get('context'):
        context_input.value = project_data['context']
    form_section <= context_input

    # Campo: Prompt
    form_section <= html.LABEL("✍️ Tu Prompt Final", Class="block font-medium text-gray-700 mb-2")
    form_section <= html.P("Escribe el prompt completo que usarías con una IA", Class="text-sm text-gray-500 mb-2")
    prompt_input = html.TEXTAREA(
        placeholder="Escribe tu prompt aquí. Usa las técnicas aprendidas: especificidad, formato, técnicas como CoT o few-shot...",
        Class="w-full h-48 p-3 border border-gray-300 rounded-xl mb-4 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 font-mono",
        id="project-prompt"
    )
    if project_data.get('prompt'):
        prompt_input.value = project_data['prompt']
    form_section <= prompt_input

    # Contador de palabras
    word_count = html.DIV("0 palabras", Class="text-sm text-gray-500 mb-6", id="prompt-word-count")
    form_section <= word_count

    # Campo: Técnica usada
    form_section <= html.LABEL("🎯 Técnica(s) aplicada(s)", Class="block font-medium text-gray-700 mb-2")
    technique_input = html.INPUT(
        type="text",
        placeholder="Ej: Chain of Thought + Role Prompting",
        Class="w-full p-3 border border-gray-300 rounded-xl mb-6 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
        id="project-technique"
    )
    if project_data.get('technique'):
        technique_input.value = project_data['technique']
    form_section <= technique_input

    # Campo: Reflexión
    form_section <= html.LABEL("💭 Reflexión", Class="block font-medium text-gray-700 mb-2")
    form_section <= html.P("¿Por qué elegiste esta técnica? ¿Qué aprendiste?", Class="text-sm text-gray-500 mb-2")
    reflection_input = html.TEXTAREA(
        placeholder="Comparte tu reflexión sobre el proceso de crear este prompt...",
        Class="w-full h-24 p-3 border border-gray-300 rounded-xl mb-6 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
        id="project-reflection"
    )
    if project_data.get('reflection'):
        reflection_input.value = project_data['reflection']
    form_section <= reflection_input

    container <= form_section

    # Botones
    buttons = html.DIV(Class="flex gap-4 justify-center")

    save_btn = html.BUTTON(
        "💾 Guardar Borrador",
        Class="px-6 py-3 bg-gray-600 text-white rounded-xl hover:bg-gray-700 font-medium"
    )
    save_btn.bind('click', lambda ev: _save_project_draft())
    buttons <= save_btn

    submit_btn = html.BUTTON(
        "🎓 Enviar Proyecto Final",
        Class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 font-medium"
    )
    submit_btn.bind('click', lambda ev: _submit_project())
    buttons <= submit_btn

    container <= buttons

    # Área de feedback
    feedback = html.DIV(id="project-feedback", Class="mt-6")
    container <= feedback

    # Actualizar contador de palabras
    def update_word_count(ev):
        text = document.getElementById("project-prompt").value
        words = len(text.split()) if text.strip() else 0
        document.getElementById("prompt-word-count").textContent = f"{words} palabras"

    prompt_input.bind('input', update_word_count)

    return container


def _calculate_course_progress(state):
    """Calcula el progreso total del curso."""
    lessons_completed = len(state.data.get('progress', {}).get('lessons_completed', []))
    puzzles_solved = state.data.get('progress', {}).get('puzzles_solved', 0)
    practice_done = len(state.data.get('practice', {}).get('completed_exercises', []))
    claude_exercises = len(state.data.get('claude_exercises', {}).get('completed', []))

    # Pesos (simplificado)
    total_lessons = 17  # Aproximado
    total_puzzles = 12
    total_practice = 8
    total_claude = 10

    weighted_progress = (
        (lessons_completed / total_lessons * 30) +
        (puzzles_solved / total_puzzles * 25) +
        (practice_done / total_practice * 25) +
        (claude_exercises / total_claude * 20)
    )

    return {
        'percentage': min(100, int(weighted_progress)),
        'lessons': lessons_completed,
        'puzzles': puzzles_solved,
        'practice': practice_done,
        'claude': claude_exercises
    }


def _save_project_draft():
    """Guarda el borrador del proyecto."""
    state = get_state()

    project_data = {
        'title': document.getElementById("project-title").value,
        'context': document.getElementById("project-context").value,
        'prompt': document.getElementById("project-prompt").value,
        'technique': document.getElementById("project-technique").value,
        'reflection': document.getElementById("project-reflection").value,
        'completed': False
    }

    state.data['final_project'] = project_data
    state.save()

    feedback = document.getElementById("project-feedback")
    feedback.innerHTML = ""
    msg = html.DIV("💾 Borrador guardado correctamente",
                   Class="bg-green-100 border border-green-300 text-green-800 rounded-xl p-4 text-center")
    feedback <= msg


def _submit_project():
    """Envía y evalúa el proyecto final."""
    state = get_state()

    title = document.getElementById("project-title").value.strip()
    context = document.getElementById("project-context").value.strip()
    prompt = document.getElementById("project-prompt").value.strip()
    technique = document.getElementById("project-technique").value.strip()
    reflection = document.getElementById("project-reflection").value.strip()

    feedback = document.getElementById("project-feedback")
    feedback.innerHTML = ""

    # Validaciones
    errors = []
    if len(title) < 5:
        errors.append("El título es muy corto")
    if len(context) < 20:
        errors.append("Describe mejor el contexto (mínimo 20 caracteres)")
    if len(prompt) < 50:
        errors.append("El prompt es muy corto (mínimo 50 caracteres)")
    if len(technique) < 3:
        errors.append("Indica qué técnica usaste")
    if len(reflection) < 20:
        errors.append("Agrega una reflexión más completa")

    if errors:
        error_msg = html.DIV(Class="bg-red-100 border border-red-300 text-red-800 rounded-xl p-4")
        error_msg <= html.P("⚠️ Por favor corrige lo siguiente:", Class="font-medium mb-2")
        error_list = html.UL(Class="list-disc list-inside")
        for err in errors:
            error_list <= html.LI(err)
        error_msg <= error_list
        feedback <= error_msg
        return

    # Evaluar el prompt
    prompt_lower = prompt.lower()
    word_count = len(prompt.split())

    evaluation = {
        'context': len(context) >= 30,
        'technique': any(t in prompt_lower for t in ['paso a paso', 'actúa como', 'ejemplo', 'eres un', 'step by step']),
        'specificity': word_count >= 30,
        'format': any(f in prompt_lower for f in ['formato', 'lista', 'tabla', 'json', 'puntos']),
        'complete': word_count >= 40 and ':' in prompt or '.' in prompt
    }

    passed = sum(evaluation.values())
    total = len(evaluation)
    score = int((passed / total) * 100)

    if score >= 60:
        # ¡Proyecto aprobado!
        project_data = {
            'title': title,
            'context': context,
            'prompt': prompt,
            'technique': technique,
            'reflection': reflection,
            'completed': True,
            'score': score,
            'evaluation': evaluation,
            'completed_at': str(window.Date.new().toISOString())
        }

        state.data['final_project'] = project_data
        state.save()

        # Dar XP y badge
        from ..gamification.xp import award_xp
        award_xp(state, 'final_project', 200, None, "Completar Proyecto Final")

        # Otorgar badge de graduación
        badges_earned = state.data.get('badges', [])
        if 'graduate' not in badges_earned:
            badges_earned.append('graduate')
            state.data['badges'] = badges_earned
            state.save()

        # Mostrar mensaje de éxito
        success = html.DIV(Class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white text-center")
        success <= html.DIV("🎓", Class="text-6xl mb-4")
        success <= html.H2("¡Felicitaciones!", Class="text-3xl font-bold mb-2")
        success <= html.P("Has completado el Proyecto Final de PromptCraft", Class="text-indigo-200 mb-4")
        success <= html.P(f"Puntuación: {score}%", Class="text-xl font-medium mb-4")
        success <= html.P("+200 XP • Badge de Graduación Desbloqueado 🏆", Class="text-indigo-200")

        continue_btn = html.A(
            "Ver mi Proyecto Completado →",
            href="#final-project",
            Class="inline-block mt-6 px-6 py-3 bg-white text-indigo-600 rounded-xl font-medium hover:bg-indigo-50"
        )
        success <= continue_btn

        feedback <= success

    else:
        # Necesita mejoras
        improve_msg = html.DIV(Class="bg-yellow-100 border border-yellow-300 rounded-xl p-6")
        improve_msg <= html.H3("⚠️ Tu proyecto necesita mejoras", Class="font-bold text-yellow-800 mb-4")
        improve_msg <= html.P(f"Puntuación actual: {score}% (necesitas 60% para aprobar)", Class="text-yellow-700 mb-4")

        eval_list = html.DIV(Class="space-y-2")
        for req in PROJECT_REQUIREMENTS:
            passed_req = evaluation.get(req['id'], False)
            item = html.DIV(Class="flex items-center gap-2")
            item <= html.SPAN("✅" if passed_req else "❌")
            item <= html.SPAN(req['name'], Class="text-yellow-800")
            eval_list <= item

        improve_msg <= eval_list
        feedback <= improve_msg


def _render_completed_project(container, project_data):
    """Renderiza el proyecto completado."""
    # Header con celebración
    header = html.DIV(Class="text-center mb-8")
    header <= html.DIV("🎓", Class="text-6xl mb-4")
    header <= html.H1("¡Proyecto Completado!", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(f"Puntuación: {project_data.get('score', 0)}%",
                     Class="text-xl text-indigo-600 font-medium")
    container <= header

    # Badge de graduación
    badge_card = html.DIV(Class="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl p-6 text-white text-center mb-8")
    badge_card <= html.DIV("🏆", Class="text-5xl mb-2")
    badge_card <= html.H3("Badge de Graduación", Class="text-xl font-bold")
    badge_card <= html.P("Has completado PromptCraft", Class="text-yellow-100")
    container <= badge_card

    # Tu proyecto
    project_card = html.DIV(Class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-8")

    project_card <= html.H2(project_data.get('title', 'Mi Proyecto'),
                            Class="text-2xl font-bold text-gray-800 mb-4")

    # Contexto
    project_card <= html.H3("📋 Contexto", Class="font-semibold text-gray-700 mb-2")
    project_card <= html.P(project_data.get('context', ''),
                           Class="text-gray-600 mb-4 bg-gray-50 p-3 rounded-lg")

    # El Prompt
    project_card <= html.H3("✍️ Tu Prompt", Class="font-semibold text-gray-700 mb-2")
    project_card <= html.PRE(project_data.get('prompt', ''),
                             Class="text-gray-600 mb-4 bg-indigo-50 p-4 rounded-lg whitespace-pre-wrap font-mono text-sm")

    # Técnica
    project_card <= html.H3("🎯 Técnica Usada", Class="font-semibold text-gray-700 mb-2")
    project_card <= html.P(project_data.get('technique', ''),
                           Class="text-gray-600 mb-4")

    # Reflexión
    project_card <= html.H3("💭 Reflexión", Class="font-semibold text-gray-700 mb-2")
    project_card <= html.P(project_data.get('reflection', ''),
                           Class="text-gray-600 italic")

    container <= project_card

    # Evaluación
    evaluation = project_data.get('evaluation', {})
    eval_card = html.DIV(Class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8")
    eval_card <= html.H3("📊 Evaluación", Class="font-bold text-gray-800 mb-4")

    for req in PROJECT_REQUIREMENTS:
        passed = evaluation.get(req['id'], False)
        item = html.DIV(Class=f"flex items-center gap-3 p-2 rounded-lg mb-2 " +
                              ("bg-green-50" if passed else "bg-gray-50"))
        item <= html.SPAN("✅" if passed else "⬜", Class="text-lg")
        item <= html.SPAN(req['name'], Class="font-medium " +
                                             ("text-green-800" if passed else "text-gray-500"))
        eval_card <= item

    container <= eval_card

    # Botones
    buttons = html.DIV(Class="flex gap-4 justify-center")
    buttons <= html.A("🏠 Volver al Inicio", href="#home",
                      Class="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 font-medium")
    buttons <= html.A("🏆 Ver Badges", href="#badges",
                      Class="px-6 py-3 border-2 border-indigo-600 text-indigo-600 rounded-xl hover:bg-indigo-50 font-medium")
    container <= buttons

    return container
