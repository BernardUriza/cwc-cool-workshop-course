# PromptCraft - Lesson Renderer
# Renderizador de contenido de lecciones

from browser import document, html


class LessonRenderer:
    """Renderiza el contenido de una lección en HTML."""

    def __init__(self, lesson_data):
        """
        Inicializa el renderer.

        Args:
            lesson_data: dict con datos de la lección
        """
        self.lesson = lesson_data
        self.sections = lesson_data.get('sections', [])

    def render(self):
        """
        Renderiza la lección completa.

        Returns:
            Elemento DOM con el contenido
        """
        container = html.DIV(Class="lesson-content space-y-8")

        # Header de la lección
        header = self._render_header()
        container <= header

        # Objetivos
        objectives = self._render_objectives()
        container <= objectives

        # Secciones de contenido
        for i, section in enumerate(self.sections):
            section_elem = self._render_section(section, i)
            container <= section_elem

        # Ejercicio
        if self.lesson.get('exercise'):
            exercise = self._render_exercise()
            container <= exercise

        return container

    def _render_header(self):
        """Renderiza el header de la lección."""
        header = html.DIV(Class="mb-8")

        # Breadcrumb
        category = self.lesson.get('category', '')
        breadcrumb = html.DIV(
            html.A("Lecciones", href="#lessons", Class="text-indigo-600 hover:underline") +
            html.SPAN(" / ", Class="text-gray-400 mx-2") +
            html.SPAN(category.title(), Class="text-gray-500"),
            Class="text-sm mb-2"
        )
        header <= breadcrumb

        # Título
        icon = self.lesson.get('icon', '📚')
        title = self.lesson.get('title', 'Lección')
        header <= html.H1(
            f"{icon} {title}",
            Class="text-3xl font-bold text-gray-800 mb-3"
        )

        # Meta información
        meta = html.DIV(Class="flex flex-wrap gap-4 text-sm text-gray-500")

        # Duración
        duration = self.lesson.get('duration', 10)
        meta <= html.SPAN(f"⏱️ {duration} min")

        # Dificultad
        difficulty = self.lesson.get('difficulty', 'beginner')
        diff_labels = {
            'beginner': ('🟢', 'Principiante'),
            'intermediate': ('🟡', 'Intermedio'),
            'advanced': ('🔴', 'Avanzado')
        }
        diff_icon, diff_label = diff_labels.get(difficulty, ('⚪', 'Desconocido'))
        meta <= html.SPAN(f"{diff_icon} {diff_label}")

        # XP
        xp = self.lesson.get('xp_reward', 0)
        meta <= html.SPAN(f"⭐ {xp} XP")

        header <= meta

        return header

    def _render_objectives(self):
        """Renderiza los objetivos de aprendizaje."""
        objectives = self.lesson.get('objectives', [])
        if not objectives:
            return html.DIV()

        section = html.DIV(Class="bg-indigo-50 rounded-xl p-6 border border-indigo-100")

        section <= html.H3(
            "🎯 Objetivos de Aprendizaje",
            Class="font-semibold text-indigo-800 mb-3"
        )

        obj_list = html.UL(Class="space-y-2")
        for obj in objectives:
            obj_list <= html.LI(
                html.SPAN("✓ ", Class="text-indigo-500 font-bold") +
                html.SPAN(obj, Class="text-indigo-700"),
                Class="flex items-start"
            )
        section <= obj_list

        return section

    def _render_section(self, section, index):
        """
        Renderiza una sección de contenido.

        Args:
            section: dict con datos de la sección
            index: índice de la sección

        Returns:
            Elemento DOM
        """
        section_type = section.get('type', 'text')

        renderers = {
            'text': self._render_text_section,
            'tip': self._render_tip_section,
            'example': self._render_example_section,
            'code': self._render_code_section,
            'warning': self._render_warning_section,
            'note': self._render_note_section,
            'quiz': self._render_quiz_section
        }

        renderer = renderers.get(section_type, self._render_text_section)
        return renderer(section)

    def _render_text_section(self, section):
        """Renderiza una sección de texto."""
        container = html.DIV(Class="prose prose-indigo max-w-none")

        title = section.get('title')
        if title:
            container <= html.H2(title, Class="text-xl font-semibold text-gray-800 mb-4")

        content = section.get('content', '')
        # Procesar markdown básico
        paragraphs = content.strip().split('\n\n')
        for para in paragraphs:
            if para.strip():
                processed = self._process_markdown(para.strip())
                container <= html.DIV(processed, Class="text-gray-700 mb-4 leading-relaxed")

        return container

    def _render_tip_section(self, section):
        """Renderiza un tip/consejo."""
        container = html.DIV(
            Class="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg"
        )

        container <= html.DIV(
            html.SPAN("💡 ", Class="text-xl") +
            html.SPAN("Tip", Class="font-semibold text-amber-800"),
            Class="mb-2"
        )

        content = section.get('content', '')
        container <= html.P(content, Class="text-amber-700")

        return container

    def _render_warning_section(self, section):
        """Renderiza una advertencia."""
        container = html.DIV(
            Class="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg"
        )

        container <= html.DIV(
            html.SPAN("⚠️ ", Class="text-xl") +
            html.SPAN("Advertencia", Class="font-semibold text-red-800"),
            Class="mb-2"
        )

        content = section.get('content', '')
        container <= html.P(content, Class="text-red-700")

        return container

    def _render_note_section(self, section):
        """Renderiza una nota."""
        container = html.DIV(
            Class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg"
        )

        container <= html.DIV(
            html.SPAN("📝 ", Class="text-xl") +
            html.SPAN("Nota", Class="font-semibold text-blue-800"),
            Class="mb-2"
        )

        content = section.get('content', '')
        container <= html.P(content, Class="text-blue-700")

        return container

    def _render_example_section(self, section):
        """Renderiza una sección de ejemplo (bueno vs malo)."""
        container = html.DIV(Class="space-y-4")

        title = section.get('title')
        if title:
            container <= html.H3(title, Class="text-lg font-semibold text-gray-800")

        # Ejemplo malo
        bad = section.get('bad_example', {})
        if bad:
            bad_card = html.DIV(Class="bg-red-50 rounded-lg p-4 border border-red-100")
            bad_card <= html.DIV(
                html.SPAN("❌ ", Class="text-lg") +
                html.SPAN("Prompt débil", Class="font-medium text-red-800"),
                Class="mb-2"
            )
            bad_card <= html.DIV(
                html.CODE(bad.get('prompt', ''), Class="text-sm"),
                Class="bg-white p-3 rounded border border-red-200 mb-2 block font-mono"
            )
            if bad.get('issue'):
                bad_card <= html.P(
                    f"⚠️ {bad['issue']}",
                    Class="text-sm text-red-600"
                )
            container <= bad_card

        # Ejemplo bueno
        good = section.get('good_example', {})
        if good:
            good_card = html.DIV(Class="bg-green-50 rounded-lg p-4 border border-green-100")
            good_card <= html.DIV(
                html.SPAN("✅ ", Class="text-lg") +
                html.SPAN("Prompt mejorado", Class="font-medium text-green-800"),
                Class="mb-2"
            )
            good_card <= html.DIV(
                html.CODE(good.get('prompt', ''), Class="text-sm whitespace-pre-wrap"),
                Class="bg-white p-3 rounded border border-green-200 mb-2 block font-mono"
            )
            if good.get('why'):
                good_card <= html.P(
                    f"✓ {good['why']}",
                    Class="text-sm text-green-600"
                )
            container <= good_card

        return container

    def _render_code_section(self, section):
        """Renderiza una sección de código."""
        container = html.DIV(Class="my-6")

        title = section.get('title')
        if title:
            container <= html.H3(title, Class="text-lg font-semibold text-gray-800 mb-3")

        language = section.get('language', 'text')
        code = section.get('code', '')

        code_block = html.DIV(Class="relative")

        # Header del código
        code_header = html.DIV(
            html.SPAN(language.upper(), Class="text-xs font-mono"),
            Class="bg-gray-700 text-gray-300 px-4 py-2 rounded-t-lg"
        )
        code_block <= code_header

        # Contenido del código
        code_content = html.PRE(
            html.CODE(code, Class=f"language-{language}"),
            Class="bg-gray-800 text-gray-100 p-4 rounded-b-lg overflow-x-auto font-mono text-sm"
        )
        code_block <= code_content

        container <= code_block

        return container

    def _render_quiz_section(self, section):
        """Renderiza una pregunta de quiz inline."""
        container = html.DIV(Class="bg-purple-50 rounded-xl p-6 border border-purple-100")

        question = section.get('question', '')
        container <= html.P(
            f"❓ {question}",
            Class="font-medium text-purple-800 mb-4"
        )

        options = section.get('options', [])
        options_div = html.DIV(Class="space-y-2")

        for i, option in enumerate(options):
            opt_btn = html.BUTTON(
                f"{chr(65 + i)}. {option}",
                Class="w-full text-left p-3 bg-white rounded-lg border border-purple-200 hover:border-purple-400 hover:bg-purple-50 transition-colors"
            )
            opt_btn.bind('click', lambda e, idx=i: self._check_answer(section, idx, e.target))
            options_div <= opt_btn

        container <= options_div

        # Área de feedback
        container <= html.DIV(id=f"quiz-feedback-{id(section)}", Class="mt-4")

        return container

    def _check_answer(self, section, selected_idx, button):
        """Verifica la respuesta del quiz."""
        correct_idx = section.get('correct', 0)
        feedback_id = f"quiz-feedback-{id(section)}"
        feedback_elem = document.getElementById(feedback_id)

        if feedback_elem:
            if selected_idx == correct_idx:
                feedback_elem.innerHTML = ""
                feedback_elem <= html.DIV(
                    html.SPAN("✅ ¡Correcto! ", Class="font-bold") +
                    html.SPAN(section.get('explanation', '')),
                    Class="p-3 bg-green-100 text-green-800 rounded-lg"
                )
                button.className = button.className.replace("border-purple-200", "border-green-500 bg-green-50")
            else:
                feedback_elem.innerHTML = ""
                feedback_elem <= html.DIV(
                    "❌ Incorrecto. Intenta de nuevo.",
                    Class="p-3 bg-red-100 text-red-800 rounded-lg"
                )
                button.className = button.className.replace("border-purple-200", "border-red-300")

    def _render_exercise(self):
        """Renderiza el ejercicio de la lección."""
        exercise = self.lesson.get('exercise', {})
        if not exercise:
            return html.DIV()

        container = html.DIV(Class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-100 mt-8")

        # Header
        container <= html.DIV(
            html.SPAN("🏋️ ", Class="text-2xl") +
            html.SPAN("Ejercicio Práctico", Class="text-xl font-bold text-indigo-800"),
            Class="mb-4"
        )

        # Instrucción
        instruction = exercise.get('instruction', '')
        container <= html.P(instruction, Class="text-gray-700 mb-4")

        # Tipo de ejercicio
        exercise_type = exercise.get('type', 'free_form')

        if exercise_type == 'improve_prompt':
            container <= self._render_improve_prompt_exercise(exercise)
        elif exercise_type == 'build_prompt':
            container <= self._render_build_prompt_exercise(exercise)
        elif exercise_type == 'create_prompt':
            container <= self._render_create_prompt_exercise(exercise)
        elif exercise_type == 'create_few_shot':
            container <= self._render_few_shot_exercise(exercise)
        else:
            container <= self._render_free_form_exercise(exercise)

        # Hints
        hints = exercise.get('hints', [])
        if hints:
            hints_div = html.DIV(Class="mt-6")
            hints_div <= html.BUTTON(
                "💡 Ver pistas",
                Class="text-indigo-600 hover:text-indigo-800 text-sm font-medium",
                id="hints-toggle"
            )
            hints_content = html.DIV(
                Class="hidden mt-3 bg-white rounded-lg p-4 border border-indigo-100",
                id="hints-content"
            )
            hints_list = html.UL(Class="space-y-1 text-sm text-gray-600")
            for hint in hints:
                hints_list <= html.LI(f"• {hint}")
            hints_content <= hints_list
            hints_div <= hints_content

            # Toggle para hints
            def toggle_hints(e):
                content = document.getElementById("hints-content")
                if content:
                    if "hidden" in content.className:
                        content.className = content.className.replace("hidden", "")
                        e.target.textContent = "🙈 Ocultar pistas"
                    else:
                        content.className += " hidden"
                        e.target.textContent = "💡 Ver pistas"

            container <= hints_div

        return container

    def _render_improve_prompt_exercise(self, exercise):
        """Renderiza ejercicio de mejorar prompt."""
        container = html.DIV()

        original = exercise.get('original_prompt', '')
        container <= html.DIV(
            html.P("Prompt original:", Class="text-sm text-gray-500 mb-1") +
            html.DIV(
                html.CODE(original, Class="text-sm"),
                Class="bg-gray-100 p-3 rounded-lg border border-gray-200 font-mono"
            ),
            Class="mb-4"
        )

        # Editor
        container <= html.P("Tu versión mejorada:", Class="text-sm text-gray-500 mb-1")
        textarea = html.TEXTAREA(
            placeholder="Escribe aquí tu versión mejorada del prompt...",
            Class="w-full h-32 p-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 font-mono text-sm",
            id="exercise-answer"
        )
        container <= textarea

        # Botón de verificar
        check_btn = html.BUTTON(
            "Verificar mi respuesta",
            Class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        )
        container <= check_btn

        return container

    def _render_build_prompt_exercise(self, exercise):
        """Renderiza ejercicio de construir prompt."""
        container = html.DIV()

        required = exercise.get('required_components', [])
        if required:
            container <= html.P(
                f"Tu prompt debe incluir: {', '.join(required)}",
                Class="text-sm text-indigo-600 mb-3"
            )

        textarea = html.TEXTAREA(
            placeholder="Construye tu prompt aquí...",
            Class="w-full h-40 p-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 font-mono text-sm",
            id="exercise-answer"
        )
        container <= textarea

        check_btn = html.BUTTON(
            "Verificar mi respuesta",
            Class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        )
        container <= check_btn

        return container

    def _render_create_prompt_exercise(self, exercise):
        """Renderiza ejercicio de crear prompt."""
        container = html.DIV()

        test_input = exercise.get('test_input')
        if test_input:
            container <= html.DIV(
                html.P("Entrada de prueba:", Class="text-sm text-gray-500 mb-1") +
                html.DIV(
                    test_input,
                    Class="bg-gray-100 p-3 rounded-lg border border-gray-200 text-sm"
                ),
                Class="mb-4"
            )

        textarea = html.TEXTAREA(
            placeholder="Escribe tu prompt aquí...",
            Class="w-full h-32 p-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 font-mono text-sm",
            id="exercise-answer"
        )
        container <= textarea

        check_btn = html.BUTTON(
            "Verificar mi respuesta",
            Class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        )
        container <= check_btn

        return container

    def _render_few_shot_exercise(self, exercise):
        """Renderiza ejercicio de few-shot."""
        container = html.DIV()

        test_case = exercise.get('test_case', {})
        if test_case:
            container <= html.DIV(
                html.P("Tu prompt debe producir esta transformación:", Class="text-sm text-gray-500 mb-1") +
                html.DIV(
                    html.SPAN("Input: ", Class="font-medium") +
                    html.SPAN(test_case.get('input', '')) +
                    html.BR() +
                    html.SPAN("Output esperado: ", Class="font-medium") +
                    html.SPAN(test_case.get('expected_output', '')),
                    Class="bg-gray-100 p-3 rounded-lg border border-gray-200 text-sm"
                ),
                Class="mb-4"
            )

        textarea = html.TEXTAREA(
            placeholder="Escribe tu prompt few-shot con ejemplos...",
            Class="w-full h-48 p-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 font-mono text-sm",
            id="exercise-answer"
        )
        container <= textarea

        check_btn = html.BUTTON(
            "Verificar mi respuesta",
            Class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        )
        container <= check_btn

        return container

    def _render_free_form_exercise(self, exercise):
        """Renderiza ejercicio de forma libre."""
        container = html.DIV()

        textarea = html.TEXTAREA(
            placeholder="Escribe tu respuesta aquí...",
            Class="w-full h-32 p-3 border border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-sm",
            id="exercise-answer"
        )
        container <= textarea

        check_btn = html.BUTTON(
            "Verificar mi respuesta",
            Class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        )
        container <= check_btn

        return container

    def _process_markdown(self, text):
        """
        Procesa markdown básico.

        Args:
            text: Texto con markdown

        Returns:
            Texto con HTML básico
        """
        # Bold
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        # Code inline
        text = re.sub(r'`(.+?)`', r'<code class="bg-gray-100 px-1 rounded">\1</code>', text)

        # Bullet points
        lines = text.split('\n')
        processed_lines = []
        in_list = False

        for line in lines:
            if line.strip().startswith('• ') or line.strip().startswith('- '):
                if not in_list:
                    processed_lines.append('<ul class="list-disc list-inside space-y-1 my-2">')
                    in_list = True
                item = line.strip()[2:]  # Quitar el bullet
                processed_lines.append(f'<li>{item}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)

        if in_list:
            processed_lines.append('</ul>')

        return '\n'.join(processed_lines)


def render_lesson_content(lesson_data):
    """
    Función helper para renderizar contenido de lección.

    Args:
        lesson_data: dict con datos de la lección

    Returns:
        Elemento DOM
    """
    renderer = LessonRenderer(lesson_data)
    return renderer.render()
