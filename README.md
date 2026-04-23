    # 🚀 AI Debugger Pro

A multi-language debugging tool with real-time analysis and AI-assisted code fixes.

AI Debugger Pro allows you to write, run, and debug code across multiple languages while receiving intelligent suggestions in a lightweight desktop interface.

---

## 🎥 Demo

![Demo](assets/demo.gif)

### What the demo shows:
- Writing buggy code
- Real-time syntax detection
- Running code across languages
- AI-generated fix suggestions
- Side-by-side diff comparison

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

## 🏗️ Architecture Overview

Core system is divided into independent modules:

- `executor.py` → Secure code execution engine
- `analyzer.py` → Python AST-based syntax validation
- `ai_suggester.py` → AI debugging + fix generation
- `languages.py` → Language registry (plugin-style design)
- `history.py` → Execution history tracking system
- `realtime.py` → Live syntax checking engine
- `gui.py` → Tkinter-based interface layer

---

## ⚙️ Installation

```bash
git clone https://github.com/Tybent18/ai-debugger-pro
cd ai-debugger-pro

pip install -r requirements.txt