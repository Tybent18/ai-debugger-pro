import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from core.ai_suggester import ai_diagnose
from core.diff import show_diff
from core.history import ExecutionHistory
from core.languages import SUPPORTED_LANGUAGES, check_syntax, run_code


class AIDebuggerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Debugger Pro")
        self.history_store = ExecutionHistory()
        self.pending_diagnosis = None
        self.pending_original_code = ""
        self.pending_run_id = None
        self._last_checked_code = ""
        self._typing_job = None
        self._typing_delay = 600
        self._ai_busy = False

        languages = list(SUPPORTED_LANGUAGES)
        self.lang_var = tk.StringVar(value=languages[0])
        tk.OptionMenu(master, self.lang_var, *languages).pack()

        self.code_text = scrolledtext.ScrolledText(master, width=100, height=20)
        self.code_text.pack(fill=tk.BOTH, expand=True)
        self.code_text.bind("<KeyRelease>", self.on_type)

        self.output_text = scrolledtext.ScrolledText(master, width=100, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        controls = tk.Frame(master)
        controls.pack(fill=tk.X)
        self.run_button = tk.Button(controls, text="Run", command=self.run_debug)
        self.run_button.pack(side=tk.LEFT)
        self.ai_button = tk.Button(
            controls, text="Diagnose", command=self.request_diagnosis_for_current_code
        )
        self.ai_button.pack(side=tk.LEFT)
        self.apply_button = tk.Button(
            controls, text="Apply + Verify", command=self.apply_and_verify, state=tk.DISABLED
        )
        self.apply_button.pack(side=tk.LEFT)
        self.reject_button = tk.Button(
            controls, text="Reject", command=self.reject_patch, state=tk.DISABLED
        )
        self.reject_button.pack(side=tk.LEFT)
        self.test_button = tk.Button(
            controls, text="Save Regression Test", command=self.save_regression_test, state=tk.DISABLED
        )
        self.test_button.pack(side=tk.LEFT)
        tk.Button(controls, text="History Diff", command=self.show_history_diff).pack(side=tk.LEFT)
        tk.Button(controls, text="Load", command=self.load_file).pack(side=tk.LEFT)
        tk.Button(controls, text="Save", command=self.save_file).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(master, textvariable=self.status_var, anchor="w").pack(fill=tk.X)

        self.history = tk.Listbox(master, width=100, height=8)
        self.history.pack(fill=tk.BOTH, expand=True)
        self.history.bind("<Double-Button-1>", self.restore_history_entry)
        self._refresh_history()

    def on_type(self, event=None):
        if self._typing_job:
            self.master.after_cancel(self._typing_job)
        self._typing_job = self.master.after(self._typing_delay, self.check_realtime_errors)

    def check_realtime_errors(self):
        code = self._source()
        if code == self._last_checked_code:
            return
        self._last_checked_code = code
        ok, message = check_syntax(self.lang_var.get(), code)
        if not ok:
            self._set_output(f"REAL-TIME ERROR:\n{message}")

    def _source(self):
        return self.code_text.get("1.0", tk.END).rstrip()

    def _set_source(self, source):
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, source)

    def _set_output(self, message):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, message)

    def _run(self, code, language):
        ok, message = check_syntax(language, code)
        return run_code(language, code) if ok else (ok, message)

    def _record(self, code, language, ok, message, event="run", parent_id=None):
        entry = self.history_store.add(
            language, code, message, ok, event=event, parent_id=parent_id
        )
        self._refresh_history()
        return entry

    def _refresh_history(self):
        self.history.delete(0, tk.END)
        for entry in self.history_store.entries:
            status = "PASS" if entry.get("success") else "FAIL"
            timestamp = entry.get("timestamp", "unknown")[:19]
            self.history.insert(
                tk.END,
                f"{timestamp} | {entry.get('event', 'run')} | {entry.get('lang')} | {status}",
            )
        if self.history_store.entries:
            self.history.see(tk.END)

    def run_debug(self):
        self._clear_proposal()
        code = self._source()
        language = self.lang_var.get()
        ok, message = self._run(code, language)
        entry = self._record(code, language, ok, message)
        self._set_output(message)
        if not ok:
            self._request_diagnosis(code, message, language, entry["id"])

    def request_diagnosis_for_current_code(self):
        self._clear_proposal()
        code = self._source()
        language = self.lang_var.get()
        ok, message = self._run(code, language)
        entry = self._record(code, language, ok, message)
        self._set_output(message)
        if ok:
            self.status_var.set("The current program passed; no failure to diagnose")
            return
        self._request_diagnosis(code, message, language, entry["id"])

    def _request_diagnosis(self, code, message, language, run_id):
        if self._ai_busy:
            self.status_var.set("A diagnosis is already running")
            return
        self._ai_busy = True
        self.ai_button.configure(state=tk.DISABLED)
        self.status_var.set("Building structured diagnosis...")

        def worker():
            diagnosis = ai_diagnose(code, message, language)
            self.master.after(
                0, lambda: self._receive_diagnosis(diagnosis, code, language, run_id)
            )

        threading.Thread(target=worker, daemon=True).start()

    def _receive_diagnosis(self, diagnosis, original_code, language, run_id):
        self._ai_busy = False
        self.ai_button.configure(state=tk.NORMAL)
        self.pending_diagnosis = diagnosis
        self.pending_original_code = original_code
        self.pending_run_id = run_id

        output = diagnosis.render()
        if diagnosis.has_patch:
            output += "\n\n--- PROPOSED DIFF ---\n"
            output += show_diff(original_code, diagnosis.corrected_code)
            self.apply_button.configure(state=tk.NORMAL)
            self.reject_button.configure(state=tk.NORMAL)
        if diagnosis.regression_test.strip():
            self.test_button.configure(state=tk.NORMAL)
        self._set_output(output)
        self.status_var.set(
            "Repair proposal ready" if diagnosis.has_patch else "Diagnosis ready; no patch available"
        )

    def apply_and_verify(self):
        if not self.pending_diagnosis or not self.pending_diagnosis.has_patch:
            return
        diagnosis = self.pending_diagnosis
        language = self.lang_var.get()
        self._set_source(diagnosis.corrected_code)
        ok, message = self._run(diagnosis.corrected_code, language)
        self._record(
            diagnosis.corrected_code,
            language,
            ok,
            message,
            event="verified_fix" if ok else "failed_fix",
            parent_id=self.pending_run_id,
        )
        result = "VERIFIED: repair passed." if ok else "REPAIR FAILED VERIFICATION."
        self._set_output(f"{result}\n\n{message}")
        self._clear_proposal()
        self.status_var.set(result)

    def reject_patch(self):
        if self.pending_diagnosis:
            self._record(
                self.pending_original_code,
                self.lang_var.get(),
                False,
                "AI repair proposal rejected by user.",
                event="rejected_fix",
                parent_id=self.pending_run_id,
            )
        self._clear_proposal()
        self.status_var.set("Repair proposal rejected; source was not changed")

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
        destination = filedialog.asksaveasfilename(
            title="Save regression test", defaultextension=extension
        )
        if destination:
            with open(destination, "w", encoding="utf-8") as test_file:
                test_file.write(self.pending_diagnosis.regression_test)
            self.status_var.set(f"Regression test saved: {destination}")

    def show_history_diff(self):
        selection = self.history.curselection()
        if selection:
            entry = self.history_store.entries[selection[0]]
            self._set_output(entry.get("diff_from_last") or "No earlier version for comparison.")
            return
        latest = self.history_store.last()
        self._set_output(
            latest.get("diff_from_last") if latest else "No execution history is available."
        )

    def restore_history_entry(self, event=None):
        selection = self.history.curselection()
        if not selection:
            return
        entry = self.history_store.entries[selection[0]]
        if messagebox.askyesno("Restore source", "Replace the editor with this historical version?"):
            self._set_source(entry.get("code", ""))
            self.lang_var.set(entry.get("lang", "Python"))
            self._clear_proposal()
            self.status_var.set("Historical source restored")

    def load_file(self):
        source_path = filedialog.askopenfilename()
        if source_path:
            with open(source_path, encoding="utf-8") as source_file:
                self._set_source(source_file.read())
            self._clear_proposal()

    def save_file(self):
        language = SUPPORTED_LANGUAGES[self.lang_var.get()]
        destination = filedialog.asksaveasfilename(defaultextension=language.extension)
        if destination:
            with open(destination, "w", encoding="utf-8") as source_file:
                source_file.write(self._source())

