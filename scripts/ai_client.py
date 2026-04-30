#!/usr/bin/env python3
"""
ai_client.py
Single import point for AI calls — uses google-genai (new SDK).
"""

import os
import sys

_api_key = os.environ.get("GEMINI_API_KEY", "")
if not _api_key:
    print("❌ GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
    sys.exit(1)

from google import genai
from google.genai import types

_client = genai.Client(api_key=_api_key)


def _llm(system: str, user: str, max_tokens: int = 1500) -> str:
    try:
        response = _client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini API error: {e}", file=sys.stderr)
        raise


def generate(system: str, user: str, max_tokens: int = 1500) -> str:
    return _llm(system=system, user=user, max_tokens=max_tokens)
