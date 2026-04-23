import threading
from core.ai_suggester import ai_suggest_fix


def stream_ai_fix(app, code, msg, lang):
    def worker():
        suggestion = ai_suggest_fix(code, msg, lang)

        def update_ui():
            app.output_text.insert("end", "\n\n--- AI FIX ---\n")
            app.output_text.insert("end", suggestion)

        app.master.after(0, update_ui)

    threading.Thread(target=worker, daemon=True).start()