import tkinter as tk
from tkinter import ttk

from interface.theme import COLORS, FONTS


class CodeEditor(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, style="Panel.TFrame")
        self.gutter = tk.Text(
            self,
            width=5,
            padx=8,
            pady=10,
            takefocus=0,
            borderwidth=0,
            state=tk.DISABLED,
            background=COLORS["gutter"],
            foreground=COLORS["muted"],
            font=FONTS["mono_small"],
        )
        self.text = tk.Text(
            self,
            wrap=tk.NONE,
            undo=True,
            padx=12,
            pady=10,
            borderwidth=0,
            insertbackground=COLORS["text"],
            selectbackground=COLORS["selection"],
            background=COLORS["editor"],
            foreground=COLORS["text"],
            font=FONTS["mono"],
        )
        self.vertical = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._scroll_y)
        self.horizontal = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(yscrollcommand=self._on_yview, xscrollcommand=self.horizontal.set)

        self.gutter.grid(row=0, column=0, sticky="ns")
        self.text.grid(row=0, column=1, sticky="nsew")
        self.vertical.grid(row=0, column=2, sticky="ns")
        self.horizontal.grid(row=1, column=1, sticky="ew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.text.bind("<KeyRelease>", self._changed, add=True)
        self.text.bind("<MouseWheel>", lambda event: self.after_idle(self.update_line_numbers))
        self.update_line_numbers()

    def _scroll_y(self, *args):
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_yview(self, first, last):
        self.vertical.set(first, last)
        self.gutter.yview_moveto(first)

    def _changed(self, event=None):
        self.update_line_numbers()

    def update_line_numbers(self):
        line_count = int(self.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(number) for number in range(1, line_count + 1))
        self.gutter.configure(state=tk.NORMAL)
        self.gutter.delete("1.0", tk.END)
        self.gutter.insert("1.0", numbers)
        self.gutter.configure(state=tk.DISABLED)

    def get(self) -> str:
        return self.text.get("1.0", tk.END).rstrip()

    def set(self, source: str):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", source)
        self.update_line_numbers()

    def bind_source(self, sequence, callback):
        self.text.bind(sequence, callback, add=True)

