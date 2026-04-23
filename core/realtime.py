import tkinter as tk
import threading
import time

class RealtimeChecker:
    """
    Monitors a Tkinter text widget and triggers a callback
    after the user stops typing (debounced real-time checking).
    """

    def __init__(self, editor_widget, callback, delay=0.6):
        self.editor = editor_widget
        self.callback = callback
        self.delay = delay

        self._last_change = time.time()
        self._last_processed = ""
        self._running = True

        self.editor.bind("<KeyRelease>", self._on_change)
        self._start_loop()

    def _on_change(self, event=None):
        self._last_change = time.time()

    def _start_loop(self):
        def loop():
            while self._running:
                time.sleep(0.2)
                if time.time() - self._last_change > self.delay:
                    try:
                        code = self.editor.get("1.0", tk.END)
                    except tk.TclError:
                        break
                    if code != self._last_processed:
                        self._last_processed = code
                        try:
                            self.callback(code)
                        except Exception:
                            pass
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def stop(self):
        self._running = False