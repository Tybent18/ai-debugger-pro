import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interface.gui import AIDebuggerGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = AIDebuggerGUI(root)
    root.mainloop()