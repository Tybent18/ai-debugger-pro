    # 🚀 AI Debugger Pro

AI Debugger Pro automatically detects, analyzes, and fixes runtime errors using execution-aware AI.

Designed as a runtime-aware debugging system—not just a static code analyzer.

Example:
Input: Broken Python function
Output: Identifies bug, traces execution, suggests fix in seconds

This is a multi-language debugging tool with real-time analysis and AI-assisted code fixes.

AI Debugger Pro allows you to write, run, and debug code across multiple languages while receiving intelligent suggestions in a lightweight desktop interface.

Why this matters:

Debugging is slow and manual.

AI Debugger Pro introduces execution-aware debugging,
reducing time to identify and fix runtime issues.

---

## 📄 Research Paper (optional)

- [Read on GitHub](docs/paper.md)
- [Download PDF](docs/ai-debugger-pro-paper.pdf)

---

Watch how a runtime error is detected, analyzed, and fixed in real time:

## 🎥 Demo

![Demo](assets/demo.gif)

## ⚡ Example

**Input**
```python
def divide(a, b):
    return a / b

print(divide(10, 0))

---

## 🖥️ Interface Preview

![GUI](assets/gui.png)

---

## 📸 Additional Screenshots

### Execution History
![History](assets/screenshots/screenshot_1.png)

### Code Fix / Diff View
![Diff](assets/screenshots/screenshot_2.png)

---

## ✨ Features

- ⚡ Real-time syntax checking (debounced, non-blocking UI)
- 🧠 AI-powered debugging suggestions
- 🖥️ Multi-language execution:
  - Python
  - C
  - C++
  - Java
- 🔍 Execution history tracking
- 🔄 Code diff comparison (before vs AI fix)
- 🧩 Modular plugin-style architecture
- 🚫 Safe execution via subprocess isolation + timeouts

---

## 🏗️ Architecture (High-Level)

Execution → Analysis → AI Reasoning → Feedback → History

Modules:
- executor.py → runs code securely
- analyzer.py → validates syntax
- ai_suggester.py → generates fixes
- history.py → tracks iterations
- gui.py → interactive interface

---

## ⚙️ Installation

```bash
git clone https://github.com/Tybent18/ai-debugger-pro
cd ai-debugger-pro

pip install -r requirements.txt

---

## ▶️ Run

python gui.py