import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.ai_suggester import ai_diagnose
from core.diff import show_diff
from core.history import ExecutionHistory
from core.languages import SUPPORTED_LANGUAGES, check_syntax, run_code
from interface.theme import COLORS, FONTS, history_values, state_color
from interface.widgets import CodeEditor


class AIDebuggerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Debugger Pro")
        self.master.geometry("1240x780")
        self.master.minsize(900, 620)
        self._configure_styles()

        self.history_store = ExecutionHistory()
        self.pending_diagnosis = None
        self.pending_original_code = ""
        self.pending_run_id = None
        self._last_checked_code = ""
        self._typing_job = None
        self._typing_delay = 600
        self._ai_busy = False

        self._build_header()
        self._build_workspace()
        self._build_status_bar()
        self._bind_shortcuts()
        self._refresh_history()
        self._set_state("Ready", "neutral")

    def _configure_styles(self):
        self.master.configure(background=COLORS["window"])
        style = ttk.Style(self.master)
        style.theme_use("clam")
        style.configure(".", background=COLORS["window"], foreground=COLORS["text"], font=FONTS["ui"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("Header.TFrame", background=COLORS["panel_alt"])
        style.configure("Title.TLabel", background=COLORS["panel_alt"], foreground=COLORS["text"], font=FONTS["heading"])
        style.configure("Muted.TLabel", background=COLORS["panel_alt"], foreground=COLORS["muted"])
        style.configure("Status.TLabel", background=COLORS["panel_alt"], foreground=COLORS["muted"], padding=(10, 6))
        style.configure("Tool.TButton", padding=(11, 7), background=COLORS["panel_alt"], foreground=COLORS["text"], borderwidth=0)
        style.map("Tool.TButton", background=[("active", COLORS["border"])])
        style.configure("Accent.TButton", padding=(12, 7), background=COLORS["accent"], foreground="#ffffff", borderwidth=0)
        style.map("Accent.TButton", background=[("active", COLORS["accent_hover"]), ("disabled", COLORS["border"])])
        style.configure("Treeview", background=COLORS["panel"], fieldbackground=COLORS["panel"], foreground=COLORS["text"], rowheight=28, borderwidth=0)
        style.map("Treeview", background=[("selected", COLORS["selection"])])
        style.configure("Treeview.Heading", background=COLORS["panel_alt"], foreground=COLORS["muted"], relief=tk.FLAT)
        style.configure("TNotebook", background=COLORS["panel"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["panel_alt"], foreground=COLORS["muted"], padding=(14, 8), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", COLORS["panel"])], foreground=[("selected", COLORS["text"])])
        style.configure("TCombobox", fieldbackground=COLORS["panel"], background=COLORS["panel"], foreground=COLORS["text"])

    def _build_header(self):
        header = ttk.Frame(self.master, style="Header.TFrame", padding=(14, 10))
        header.pack(fill=tk.X)
        ttk.Label(header, text="◆  AI Debugger Pro", style="Title.TLabel").pack(side=tk.LEFT)

        self.run_button = ttk.Button(header, text="▶ Run  F5", style="Accent.TButton", command=self.run_debug)
        self.run_button.pack(side=tk.LEFT, padx=(24, 6))
        self.ai_button = ttk.Button(header, text="Diagnose  Ctrl+D", style="Tool.TButton", command=self.request_diagnosis_for_current_code)
        self.ai_button.pack(side=tk.LEFT, padx=3)
        self.apply_button = ttk.Button(header, text="Apply + Verify", style="Tool.TButton", command=self.apply_and_verify, state=tk.DISABLED)
        self.apply_button.pack(side=tk.LEFT, padx=3)
        self.reject_button = ttk.Button(header, text="Reject", style="Tool.TButton", command=self.reject_patch, state=tk.DISABLED)
        self.reject_button.pack(side=tk.LEFT, padx=3)

        self.backend_var = tk.StringVar(value=os.getenv("AI_DEBUGGER_EXECUTION_BACKEND", "docker").title())
        ttk.Label(header, textvariable=self.backend_var, style="Muted.TLabel").pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Label(header, text="● Backend", style="Muted.TLabel").pack(side=tk.RIGHT)
        self.lang_var = tk.StringVar(value=next(iter(SUPPORTED_LANGUAGES)))
        ttk.Combobox(header, textvariable=self.lang_var, values=list(SUPPORTED_LANGUAGES), state="readonly", width=9).pack(side=tk.RIGHT, padx=12)

    def _build_workspace(self):
        horizontal = ttk.Panedwindow(self.master, orient=tk.HORIZONTAL)
        horizontal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        sidebar = ttk.Frame(horizontal, style="Panel.TFrame", width=310)
        main_area = ttk.Panedwindow(horizontal, orient=tk.VERTICAL)
        horizontal.add(sidebar, weight=1)
        horizontal.add(main_area, weight=4)

        ttk.Label(sidebar, text="EXECUTION HISTORY", style="Muted.TLabel").pack(fill=tk.X, padx=10, pady=(10, 6))
        self.history = ttk.Treeview(sidebar, columns=("time", "language", "event", "status"), show="headings", selectmode="browse")
        for column, width in (("time", 125), ("language", 70), ("event", 105), ("status", 70)):
            self.history.heading(column, text=column.title())
            self.history.column(column, width=width, minwidth=55, stretch=True)
        self.history.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.history.bind("<Double-Button-1>", self.restore_history_entry)

        editor_panel = ttk.Frame(main_area, style="Panel.TFrame")
        ttk.Label(editor_panel, text="EDITOR", style="Muted.TLabel").pack(fill=tk.X, padx=10, pady=(7, 4))
        self.editor = CodeEditor(editor_panel)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind_source("<KeyRelease>", self.on_type)

        results_panel = ttk.Frame(main_area, style="Panel.TFrame")
        self.results = ttk.Notebook(results_panel)
        self.results.pack(fill=tk.BOTH, expand=True)
        self.result_views = {}
        for key, title in (("output", "Output"), ("diagnosis", "Diagnosis"), ("diff", "Proposed Diff"), ("test", "Regression Test")):
            view = tk.Text(self.results, wrap=tk.NONE, padx=12, pady=10, borderwidth=0, background=COLORS["editor"], foreground=COLORS["text"], insertbackground=COLORS["text"], selectbackground=COLORS["selection"], font=FONTS["mono_small"])
            self.results.add(view, text=title)
            self.result_views[key] = view

        test_bar = ttk.Frame(results_panel, style="Panel.TFrame")
        test_bar.pack(fill=tk.X)
        self.test_button = ttk.Button(test_bar, text="Save Regression Test", style="Tool.TButton", command=self.save_regression_test, state=tk.DISABLED)
        self.test_button.pack(side=tk.RIGHT, padx=6, pady=4)
        ttk.Button(test_bar, text="Show History Diff", style="Tool.TButton", command=self.show_history_diff).pack(side=tk.RIGHT, padx=3, pady=4)
        ttk.Button(test_bar, text="Open", style="Tool.TButton", command=self.load_file).pack(side=tk.LEFT, padx=6, pady=4)
        ttk.Button(test_bar, text="Save", style="Tool.TButton", command=self.save_file).pack(side=tk.LEFT, padx=3, pady=4)

        main_area.add(editor_panel, weight=3)
        main_area.add(results_panel, weight=2)

    def _build_status_bar(self):
        footer = ttk.Frame(self.master, style="Header.TFrame")
        footer.pack(fill=tk.X)
        self.state_dot = tk.Label(footer, text="●", background=COLORS["panel_alt"], foreground=COLORS["muted"])
        self.state_dot.pack(side=tk.LEFT, padx=(10, 0))
        self.status_var = tk.StringVar()
        ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel").pack(side=tk.LEFT)
        ttk.Label(footer, text="Ctrl+O Open   Ctrl+S Save", style="Status.TLabel").pack(side=tk.RIGHT)

    def _bind_shortcuts(self):
        self.master.bind("<F5>", lambda event: self.run_debug())
        self.master.bind("<Control-d>", lambda event: self.request_diagnosis_for_current_code())
        self.master.bind("<Control-Return>", lambda event: self.apply_and_verify())
        self.master.bind("<Control-o>", lambda event: self.load_file())
        self.master.bind("<Control-s>", lambda event: self.save_file())

    def _set_state(self, message, state="neutral"):
        self.status_var.set(message)
        self.state_dot.configure(foreground=state_color(state))

    def _set_result(self, key, message, select=False):
        view = self.result_views[key]
        view.delete("1.0", tk.END)
        view.insert("1.0", message)
        if select:
            self.results.select(view)

    def on_type(self, event=None):
        if self._typing_job:
            self.master.after_cancel(self._typing_job)
        self._typing_job = self.master.after(self._typing_delay, self.check_realtime_errors)

    def check_realtime_errors(self):
        code = self.editor.get()
        if code == self._last_checked_code:
            return
        self._last_checked_code = code
        ok, message = check_syntax(self.lang_var.get(), code)
        if not ok:
            self._set_result("output", f"REAL-TIME ERROR:\n{message}", True)
            self._set_state("Syntax issue detected", "warning")

    def _run(self, code, language):
        ok, message = check_syntax(language, code)
        return run_code(language, code) if ok else (ok, message)

    def _record(self, code, language, ok, message, event="run", parent_id=None):
        entry = self.history_store.add(language, code, message, ok, event=event, parent_id=parent_id)
        self._refresh_history()
        return entry

    def _refresh_history(self):
        for row in self.history.get_children():
            self.history.delete(row)
        for index, entry in enumerate(self.history_store.entries):
            tag = "pass" if entry.get("success") else "fail"
            self.history.insert("", tk.END, iid=str(index), values=history_values(entry), tags=(tag,))
        self.history.tag_configure("pass", foreground=COLORS["success"])
        self.history.tag_configure("fail", foreground=COLORS["danger"])
        rows = self.history.get_children()
        if rows:
            self.history.see(rows[-1])

    def run_debug(self):
        self._clear_proposal()
        code, language = self.editor.get(), self.lang_var.get()
        self._set_state("Executing in restricted backend...", "busy")
        ok, message = self._run(code, language)
        entry = self._record(code, language, ok, message)
        self._set_result("output", message, True)
        self._set_state("Execution passed" if ok else "Execution failed", "success" if ok else "failure")
        if not ok:
            self._request_diagnosis(code, message, language, entry["id"])

    def request_diagnosis_for_current_code(self):
        self._clear_proposal()
        code, language = self.editor.get(), self.lang_var.get()
        ok, message = self._run(code, language)
        entry = self._record(code, language, ok, message)
        self._set_result("output", message)
        if ok:
            self._set_state("Program passed; no failure to diagnose", "success")
            return
        self._request_diagnosis(code, message, language, entry["id"])

    def _request_diagnosis(self, code, message, language, run_id):
        if self._ai_busy:
            return
        self._ai_busy = True
        self.ai_button.configure(state=tk.DISABLED)
        self._set_state("Building structured diagnosis...", "busy")

        def worker():
            diagnosis = ai_diagnose(code, message, language)
            self.master.after(0, lambda: self._receive_diagnosis(diagnosis, code, language, run_id))

        threading.Thread(target=worker, daemon=True).start()

    def _receive_diagnosis(self, diagnosis, original_code, language, run_id):
        self._ai_busy = False
        self.ai_button.configure(state=tk.NORMAL)
        self.pending_diagnosis = diagnosis
        self.pending_original_code = original_code
        self.pending_run_id = run_id
        self._set_result("diagnosis", diagnosis.render(), True)
        if diagnosis.has_patch:
            self._set_result("diff", show_diff(original_code, diagnosis.corrected_code))
            self.apply_button.configure(state=tk.NORMAL)
            self.reject_button.configure(state=tk.NORMAL)
        if diagnosis.regression_test.strip():
            self._set_result("test", diagnosis.regression_test)
            self.test_button.configure(state=tk.NORMAL)
        self._set_state("Repair proposal ready" if diagnosis.has_patch else "Diagnosis ready; no patch available", "warning")

    def apply_and_verify(self):
        if not self.pending_diagnosis or not self.pending_diagnosis.has_patch:
            return
        diagnosis, language = self.pending_diagnosis, self.lang_var.get()
        self.editor.set(diagnosis.corrected_code)
        ok, message = self._run(diagnosis.corrected_code, language)
        self._record(diagnosis.corrected_code, language, ok, message, event="verified_fix" if ok else "failed_fix", parent_id=self.pending_run_id)
        self._set_result("output", ("VERIFIED REPAIR\n\n" if ok else "REPAIR FAILED VERIFICATION\n\n") + message, True)
        self._clear_proposal()
        self._set_state("Repair verified" if ok else "Repair failed verification", "success" if ok else "failure")

    def reject_patch(self):
        if self.pending_diagnosis:
            self._record(self.pending_original_code, self.lang_var.get(), False, "AI repair proposal rejected by user.", event="rejected_fix", parent_id=self.pending_run_id)
        self._clear_proposal()
        self._set_state("Proposal rejected; source unchanged", "neutral")

    def _clear_proposal(self):
        self.pending_diagnosis = None
        self.pending_original_code = ""
        self.pending_run_id = None
        self.apply_button.configure(state=tk.DISABLED)
        self.reject_button.configure(state=tk.DISABLED)
        self.test_button.configure(state=tk.DISABLED)

    def save_regression_test(self):
        if not self.pending_diagnosis or not self.pending_diagnosis.regression_test.strip():
            return
        extension = ".py" if self.lang_var.get() == "Python" else ".txt"
        destination = filedialog.asksaveasfilename(title="Save regression test", defaultextension=extension)
        if destination:
            with open(destination, "w", encoding="utf-8") as test_file:
                test_file.write(self.pending_diagnosis.regression_test)
            self._set_state(f"Regression test saved: {destination}", "success")

    def show_history_diff(self):
        selection = self.history.selection()
        entry = self.history_store.entries[int(selection[0])] if selection else self.history_store.last()
        self._set_result("diff", entry.get("diff_from_last") if entry else "No execution history.", True)

    def restore_history_entry(self, event=None):
        selection = self.history.selection()
        if not selection:
            return
        entry = self.history_store.entries[int(selection[0])]
        if messagebox.askyesno("Restore source", "Replace the editor with this historical version?"):
            self.editor.set(entry.get("code", ""))
            self.lang_var.set(entry.get("lang", "Python"))
            self._clear_proposal()
            self._set_state("Historical source restored", "neutral")

    def load_file(self):
        source_path = filedialog.askopenfilename()
        if source_path:
            with open(source_path, encoding="utf-8") as source_file:
                self.editor.set(source_file.read())
            self._clear_proposal()
            self._set_state(f"Opened {source_path}", "neutral")

    def save_file(self):
        language = SUPPORTED_LANGUAGES[self.lang_var.get()]
        destination = filedialog.asksaveasfilename(defaultextension=language.extension)
        if destination:
            with open(destination, "w", encoding="utf-8") as source_file:
                source_file.write(self.editor.get())
            self._set_state(f"Saved {destination}", "success")
