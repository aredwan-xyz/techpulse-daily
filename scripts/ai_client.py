#!/usr/bin/env python3
"""
ai_client.py
Multi-provider AI client with automatic fallback.
Priority: Gemini (2.0-flash → 1.5-flash) → Groq → GitHub Models
"""

import os
import sys

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

_GEMINI_MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]
_GROQ_MODEL = "llama-3.3-70b-versatile"
_GITHUB_MODEL = "gpt-4o-mini"


def _is_quota_error(e: Exception) -> bool:
    msg = str(e)
    return any(k in msg for k in ("429", "RESOURCE_EXHAUSTED", "quota", "rate limit"))


def _call_gemini(system: str, user: str, max_tokens: int) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)
    last_err = None
    for model in _GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=max_tokens,
                ),
            )
            print(f"✅ Used Gemini ({model})")
            return response.text
        except Exception as e:
            if _is_quota_error(e):
                print(f"⚠️  Gemini {model} quota exceeded, trying next model...", file=sys.stderr)
                last_err = e
                continue
            raise
    raise last_err


def _call_openai_compat(base_url: str, api_key: str, model: str,
                         system: str, user: str, max_tokens: int) -> str:
    from openai import OpenAI

    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _llm(system: str, user: str, max_tokens: int = 1500) -> str:
    errors = []

    if GEMINI_API_KEY:
        try:
            return _call_gemini(system, user, max_tokens)
        except Exception as e:
            print(f"⚠️  Gemini failed: {e}", file=sys.stderr)
            errors.append(f"Gemini: {e}")

    if GROQ_API_KEY:
        try:
            result = _call_openai_compat(
                "https://api.groq.com/openai/v1", GROQ_API_KEY, _GROQ_MODEL,
                system, user, max_tokens,
            )
            print(f"✅ Used Groq ({_GROQ_MODEL})")
            return result
        except Exception as e:
            print(f"⚠️  Groq failed: {e}", file=sys.stderr)
            errors.append(f"Groq: {e}")

    if GITHUB_TOKEN:
        try:
            result = _call_openai_compat(
                "https://models.inference.ai.azure.com", GITHUB_TOKEN, _GITHUB_MODEL,
                system, user, max_tokens,
            )
            print(f"✅ Used GitHub Models ({_GITHUB_MODEL})")
            return result
        except Exception as e:
            print(f"⚠️  GitHub Models failed: {e}", file=sys.stderr)
            errors.append(f"GitHub Models: {e}")

    print("❌ All AI providers exhausted.", file=sys.stderr)
    for err in errors:
        print(f"  • {err}", file=sys.stderr)
    sys.exit(1)


def generate(system: str, user: str, max_tokens: int = 1500) -> str:
    return _llm(system=system, user=user, max_tokens=max_tokens)
