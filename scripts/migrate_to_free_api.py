#!/usr/bin/env python3
"""Retired migration command. Provider selection no longer rewrites source files."""

import sys


if __name__ == "__main__":
    print(
        "This migration command is retired. Configure GEMINI_API_KEY or GROQ_API_KEY "
        "and optional GEMINI_MODEL/GROQ_MODEL. See README.md; no files were changed.",
        file=sys.stderr,
    )
    sys.exit(2)
