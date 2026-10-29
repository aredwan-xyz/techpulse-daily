#!/usr/bin/env python3
"""Bounded Gemini → optional Groq text generation; callers own exit status."""

import os
import time


class GenerationError(RuntimeError):
    """No configured provider returned usable content."""


def _status(error):
    for attr in ("status_code", "code"):
        try:
            return int(getattr(error, attr))
        except (TypeError, ValueError, AttributeError):
            pass
    return None


def _retry(call):
    # Three attempts maximum; SDK retries are disabled below.
    for attempt in range(3):
        try:
            return call()
        except Exception as error:
            retryable = _status(error) in (408, 429, 500, 502, 503, 504)
            retryable |= isinstance(error, (TimeoutError, ConnectionError))
            if not retryable or attempt == 2:
                raise
            time.sleep(2 ** attempt)


def _call_gemini(system, user, max_tokens):
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options=types.HttpOptions(
            api_version="v1", timeout=60000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )
    try:
        return _retry(lambda: client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system, max_output_tokens=max_tokens,
            ),
        )).text
    finally:
        client.close()


def _call_groq(system, user, max_tokens):
    from openai import OpenAI

    with OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ["GROQ_API_KEY"], timeout=60, max_retries=0,
    ) as client:
        response = _retry(lambda: client.chat.completions.create(
            model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            max_tokens=max_tokens,
        ))
        return response.choices[0].message.content


def check_configuration():
    if not any(os.environ.get(name, "").strip()
               for name in ("GEMINI_API_KEY", "GROQ_API_KEY")):
        raise GenerationError("Configure GEMINI_API_KEY or GROQ_API_KEY in Actions secrets.")


def generate(system: str, user: str, max_tokens: int = 1500) -> str:
    check_configuration()
    errors = []
    for provider, key, call in (("Gemini", "GEMINI_API_KEY", _call_gemini),
                                ("Groq", "GROQ_API_KEY", _call_groq)):
        if not os.environ.get(key, "").strip():
            continue
        try:
            text = call(system, user, max_tokens)
            if not isinstance(text, str) or len(text.strip()) < 80:
                raise GenerationError("Empty or insufficient provider response")
            print(f"Used {provider}")
            return text.strip()
        except Exception as error:
            # Do not log raw provider request/response bodies or credentials.
            status = _status(error)
            errors.append(f"{provider}: {type(error).__name__}" + (f" ({status})" if status else ""))
    raise GenerationError("All configured providers failed: " + "; ".join(errors))
