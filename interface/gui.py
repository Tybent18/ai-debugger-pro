import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext

from core.diff import show_diff
from core.history import ExecutionHistory
from core.languages import SUPPORTED_LANGUAGES, check_syntax, run_code

from core.ai_suggester import ai_suggest_fix


class AIDebuggerGUI:
    def __init__(self, master):
        self.master = master
        master.title("AI Debugger Pro")

        self.history_store = ExecutionHistory()
        self._last_checked_code = ""
        self._typing_job = None
        self._typing_delay = 600
        self._ai_busy = False

        langs = list(SUPPORTED_LANGUAGES.keys())
        self.lang_var = tk.StringVar(value=langs[0])
        tk.OptionMenu(master, self.lang_var, *langs).pack()

        self.code_text = scrolledtext.ScrolledText(master, width=90, height=20)
        self.code_text.pack()
        self.code_text.bind("<KeyRelease>", self.on_type)

        self.output_text = scrolledtext.ScrolledText(master, width=90, height=15)
        self.output_text.pack()

        self.run_button = tk.Button(master, text="Run", command=self.run_debug)
        self.run_button.pack()
        self.ai_button = tk.Button(master, text="Get AI Suggestion", command=self.auto_fix)
        self.ai_button.pack()
        tk.Button(master, text="Show Diff", command=self.show_diff).pack()
        tk.Button(master, text="Load File", command=self.load_file).pack()
        tk.Button(master, text="Save File", command=self.save_file).pack()

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(master, textvariable=self.status_var).pack()

        self.history = tk.Listbox(master, width=90)
        self.history.pack()

    def on_type(self, event=None):
        if self._typing_job:
            self.master.after_cancel(self._typing_job)
        self._typing_job = self.master.after(self._typing_delay, self.check_realtime_errors)

    def check_realtime_errors(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()
        if code == self._last_checked_code:
            return
        self._last_checked_code = code
        ok, msg = check_syntax(lang, code)
        if not ok:
            self._set_output(f"REAL-TIME ERROR:\n{msg}")

    def _set_output(self, message):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, message)

    def _append_output(self, message):
        self.output_text.insert(tk.END, message)

    def _request_ai(self, code, message, language):
        if self._ai_busy:
            self.status_var.set("An AI request is already running")
            return

        self._ai_busy = True
        self.ai_button.configure(state=tk.DISABLED)
        self.status_var.set("Requesting AI suggestion...")

        def worker():
            suggestion = ai_suggest_fix(code, message, language)

            def finish():
                self._append_output("\n\n--- AI SUGGESTION (NOT YET VERIFIED) ---\n")
                self._append_output(suggestion)
                self._ai_busy = False
                self.ai_button.configure(state=tk.NORMAL)
                self.status_var.set("Ready")

            self.master.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def run_debug(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()

        ok, msg = check_syntax(lang, code)
        if ok:
            ok, msg = run_code(lang, code)

        self.history_store.add(lang, code, msg, ok)
        self._set_output(msg)
        self.history.insert(tk.END, f"{lang}: {msg[:60]}")

        if not ok:
            self._request_ai(code, msg, lang)

    def auto_fix(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()

        ok, msg = check_syntax(lang, code)
        if ok:
            ok, msg = run_code(lang, code)
        self._set_output(msg)
        if ok:
            self.status_var.set("No detected error to send for AI analysis")
            return
        self._request_ai(code, msg, lang)

    def show_diff(self):
        if len(self.history_store.entries) < 2:
            self._set_output("Not enough history for diff.")
            return
        old = self.history_store.entries[-2]["code"]
        new = self.history_store.entries[-1]["code"]
        self._set_output(f"--- CODE DIFF ---\n{show_diff(old, new)}")

    def load_file(self):
        file = filedialog.askopenfilename()
        if file:
            with open(file, "r", encoding="utf-8") as source:
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert(tk.END, source.read())

    def save_file(self):
        language = SUPPORTED_LANGUAGES[self.lang_var.get()]
        file = filedialog.asksaveasfilename(defaultextension=language.extension)
        if file:
            with open(file, "w", encoding="utf-8") as destination:
                destination.write(self.code_text.get("1.0", tk.END))
