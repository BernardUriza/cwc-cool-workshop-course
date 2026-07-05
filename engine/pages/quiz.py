# CWC - Retrieval Quiz Page

from browser import document, html, window, timer
from ..state import get_state
from ..router import navigate
from ..gamification.xp import award_xp
from ..retrieval.sampler import sample_quiz

XP_PER_CORRECT = 10


def quiz_page(params):
    state = get_state()
    questions = sample_quiz(state)

    container = html.DIV(Class="max-w-3xl mx-auto")

    header = html.DIV(Class="mb-8")
    header <= html.H1("🧠 Quiz de Repaso", Class="text-3xl font-bold text-gray-800 mb-2")
    header <= html.P(
        "Retrieval practice: recordar activamente vence a re-leer. "
        "Mezcla de lo último que cubriste con material más viejo.",
        Class="text-gray-600"
    )
    container <= header

    if not questions:
        container <= html.DIV(
            html.SPAN("📭", Class="text-5xl block mb-4") +
            html.P("Todavía no hay nada que repasar.", Class="text-gray-600 font-medium") +
            html.P("Completa tu primera lección y regresa.", Class="text-gray-500 text-sm mt-1") +
            html.A("→ Ir a Lecciones", href="#lessons", Class="inline-block mt-4 text-indigo-600 hover:text-indigo-800"),
            Class="bg-white rounded-xl p-10 border border-gray-100 text-center"
        )
        return container

    answers = {}

    quiz_box = html.DIV(Class="space-y-6")

    for i, q in enumerate(questions):
        card = html.DIV(Class="bg-white rounded-xl p-6 border border-gray-100")
        card <= html.P(f"Pregunta {i + 1} de {len(questions)}", Class="text-xs text-gray-400 mb-2")
        card <= html.H3(q['question'], Class="text-lg font-medium text-gray-800 mb-4")

        options_box = html.DIV(Class="space-y-2", id=f"quiz-q{i}")
        for j, option in enumerate(q['options']):
            opt = html.BUTTON(
                option,
                Class="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors text-gray-700"
            )

            def on_pick(e, qi=i, oi=j):
                answers[qi] = oi
                box = document.getElementById(f"quiz-q{qi}")
                for k, child in enumerate(box.children):
                    if k == oi:
                        child.className = "w-full text-left px-4 py-3 rounded-lg border-2 border-indigo-500 bg-indigo-50 text-indigo-800 font-medium"
                    else:
                        child.className = "w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors text-gray-700"

            opt.bind('click', on_pick)
            options_box <= opt
        card <= options_box
        quiz_box <= card

    container <= quiz_box

    result_box = html.DIV(id="quiz-result", Class="mt-6")
    container <= result_box

    submit = html.BUTTON(
        "Calificar",
        Class="mt-6 w-full px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
    )

    def on_submit(e):
        if len(answers) < len(questions):
            missing = len(questions) - len(answers)
            result_box.innerHTML = ""
            result_box <= html.P(
                f"Te faltan {missing} pregunta(s) por contestar.",
                Class="text-amber-600 text-center font-medium"
            )
            return

        correct = 0
        for i, q in enumerate(questions):
            box = document.getElementById(f"quiz-q{i}")
            right = q['answer']
            picked = answers[i]
            if picked == right:
                correct += 1
            for k, child in enumerate(box.children):
                if k == right:
                    child.className = "w-full text-left px-4 py-3 rounded-lg border-2 border-green-500 bg-green-50 text-green-800 font-medium"
                elif k == picked:
                    child.className = "w-full text-left px-4 py-3 rounded-lg border-2 border-red-400 bg-red-50 text-red-700"
                child.disabled = True

        score_pct = round(correct / len(questions) * 100)
        xp = correct * XP_PER_CORRECT

        retrieval = state.data.setdefault('retrieval', {'runs': []})
        retrieval['runs'].append({'score': score_pct, 'total': len(questions), 'correct': correct})
        state.save()

        if xp:
            award_xp(state, 'quiz_complete', base_amount=xp, reason="Quiz de repaso")

        result_box.innerHTML = ""
        verdict_color = "text-green-700 bg-green-50 border-green-200" if score_pct >= 70 else "text-amber-700 bg-amber-50 border-amber-200"
        verdict_msg = "Sólido. El material sigue vivo." if score_pct >= 70 else "Menos de 70%: re-estudia las lecciones de las preguntas falladas antes de avanzar."
        result_box <= html.DIV(
            html.P(f"{correct}/{len(questions)} correctas ({score_pct}%) · +{xp} XP", Class="text-xl font-bold mb-1") +
            html.P(verdict_msg, Class="text-sm"),
            Class=f"rounded-xl p-6 border text-center {verdict_color}"
        )

        submit.remove()

    submit.bind('click', on_submit)
    container <= submit

    timer.set_timeout(lambda: window.renderMath('app'), 200)

    return container
