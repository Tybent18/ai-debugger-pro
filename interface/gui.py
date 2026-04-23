import tkinter as tk
from tkinter import scrolledtext, filedialog
import sys
import os

# ---------------------------------------------------------
# Safe project root handling
# ---------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.languages import run_code, check_syntax, SUPPORTED_LANGUAGES
from core.ai_suggester import ai_suggest_fix
from core.history import ExecutionHistory
from core.diff import show_diff


class AIDebuggerGUI:
    def __init__(self, master):
        self.master = master
        master.title("AI Debugger Pro")

        # -------------------------
        # History system
        # -------------------------
        self.history_store = ExecutionHistory()

        # -------------------------
        # REAL-TIME DEBUG STATE (NEW)
        # -------------------------
        self._last_checked_code = ""
        self._typing_job = None
        self._typing_delay = 600  # ms

        # -------------------------
        # Language selector
        # -------------------------
        langs = list(SUPPORTED_LANGUAGES.keys())
        self.lang_var = tk.StringVar(value=langs[0])
        tk.OptionMenu(master, self.lang_var, *langs).pack()

        # -------------------------
        # Code editor
        # -------------------------
        self.code_text = scrolledtext.ScrolledText(master, width=90, height=20)
        self.code_text.pack()

        # Bind real-time typing
        self.code_text.bind("<KeyRelease>", self.on_type)

        # -------------------------
        # Output panel
        # -------------------------
        self.output_text = scrolledtext.ScrolledText(master, width=90, height=15)
        self.output_text.pack()

        # -------------------------
        # Buttons
        # -------------------------
        tk.Button(master, text="Run", command=self.run_debug).pack()
        tk.Button(master, text="Auto Fix", command=self.auto_fix).pack()
        tk.Button(master, text="Show Diff", command=self.show_diff).pack()
        tk.Button(master, text="Load File", command=self.load_file).pack()
        tk.Button(master, text="Save File", command=self.save_file).pack()

        # -------------------------
        # History list
        # -------------------------
        self.history = tk.Listbox(master, width=90)
        self.history.pack()

    # =====================================================
    # REAL-TIME ERROR CHECKER (RESTORED FEATURE)
    # =====================================================
    def on_type(self, event=None):
        # cancel previous scheduled check
        if self._typing_job:
            self.master.after_cancel(self._typing_job)

        # schedule new check (debounce)
        self._typing_job = self.master.after(self._typing_delay, self.check_realtime_errors)

    def check_realtime_errors(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()

        # avoid redundant checks
        if code == self._last_checked_code:
            return

        self._last_checked_code = code

        ok, msg = check_syntax(lang, code)

        # Only show errors (not success spam)
        if not ok:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"⚠ REAL-TIME ERROR:\n{msg}")

    # =====================================================
    # RUN CODE
    # =====================================================
    def run_debug(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()

        try:
            ok, msg = check_syntax(lang, code)
            if not ok:
                raise ValueError(msg)

            ok, msg = run_code(lang, code)

        except Exception as e:
            ok = False
            msg = str(e)

        self.history_store.add(lang, code, msg, ok)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, msg)

        self.history.insert(tk.END, f"{lang}: {msg[:60]}")

        if not ok:
            suggestion = ai_suggest_fix(code, msg, lang)
            self.output_text.insert(tk.END, "\n\n--- AI FIX ---\n")
            self.output_text.insert(tk.END, suggestion)

    # =====================================================
    # AUTO FIX
    # =====================================================
    def auto_fix(self):
        code = self.code_text.get("1.0", tk.END)
        lang = self.lang_var.get()

        ok, msg = check_syntax(lang, code)

        suggestion = ai_suggest_fix(code, msg, lang)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, suggestion)

        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, suggestion)

    # =====================================================
    # DIFF VIEWER
    # =====================================================
    def show_diff(self):
        if len(self.history_store.entries) < 2:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "Not enough history for diff.")
            return

        old = self.history_store.entries[-2]["code"]
        new = self.history_store.entries[-1]["code"]

        diff_result = show_diff(old, new)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "--- CODE DIFF ---\n")
        self.output_text.insert(tk.END, diff_result)

    # =====================================================
    # FILE OPS
    # =====================================================
    def load_file(self):
        file = filedialog.askopenfilename()
        if file:
            with open(file, "r", encoding="utf-8") as f:
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert(tk.END, f.read())

    def save_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".py")
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(self.code_text.get("1.0", tk.END))