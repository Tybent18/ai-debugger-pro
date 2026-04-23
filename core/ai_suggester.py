from openai import OpenAI

client = OpenAI()

# ---------------------------------------------------------
# Offline fallback (guarantees your app never crashes)
# ---------------------------------------------------------
def offline_fix(code_text: str, error_msg: str, language: str) -> str:
    return f"""
[OFFLINE MODE - NO API AVAILABLE]

Language: {language}

Possible issue detected:
{error_msg}

Suggestion:
- Check syntax near the error line
- Ensure correct indentation
- Verify function/variable names
- Re-run after fixing obvious typos

Code preview (first 200 chars):
{code_text[:200]}
"""


# ---------------------------------------------------------
# MAIN AI FIX FUNCTION (with fallback chain)
# ---------------------------------------------------------
def ai_suggest_fix(code_text, error_msg, language="Python"):
    if not code_text or not error_msg:
        return "Missing code or error message."

    prompt = f"""
You are a debugging assistant.

Language: {language}

Code:
{code_text}

Error:
{error_msg}

Explain the issue briefly and provide corrected code.
"""

    # -----------------------------------------------------
    # 1. Try best model first
    # -----------------------------------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise debugging assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        error_str = str(e).lower()

        # -------------------------------------------------
        # 2. QUOTA / LIMIT HIT → fallback model
        # -------------------------------------------------
        if "quota" in error_str or "429" in error_str or "insufficient" in error_str:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a debugging assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=400
                )

                return response.choices[0].message.content.strip()

            except Exception:
                # fallback to offline if even this fails
                return offline_fix(code_text, error_msg, language)

        # -------------------------------------------------
        # 3. ALL OTHER ERRORS → offline mode
        # -------------------------------------------------
        return offline_fix(code_text, error_msg, language)