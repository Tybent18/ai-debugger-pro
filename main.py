import tkinter as tk

from interface.gui import AIDebuggerGUI


def main():
    root = tk.Tk()
    AIDebuggerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

