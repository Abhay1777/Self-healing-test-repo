import json
import os

from openai import OpenAI


class DebugAgent:

    def __init__(self):

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "OPENAI_API_KEY is missing. "
                "Check your .env file."
            )

        self.client = OpenAI(
            api_key=api_key
        )


    def diagnose(
        self,
        source_code,
        test_output,
        file_name
    ):

        extension = (
            file_name.split(".")[-1]
            if "." in file_name
            else "unknown"
        )

        prompt = f"""
You are Agent 2 of Self-Heal Git.

You are an autonomous software debugging agent.

Your job is to diagnose a failing software project and
propose the smallest safe correction.

TARGET FILE:
{file_name}

LANGUAGE / EXTENSION:
{extension}

SOURCE CODE:
----------------
{source_code}
----------------

TEST / BUILD / LINT FAILURE:
----------------
{test_output}
----------------

Return ONLY valid JSON.

Required structure:

{{
    "diagnosis": "brief explanation of the root cause",
    "file": "{file_name}",
    "line": 1,
    "old_code": "exact code that exists in the source",
    "new_code": "replacement code",
    "reason": "why this fixes the root cause"
}}

Rules:

1. Fix source code, never modify tests unless absolutely necessary.
2. Make the smallest possible change.
3. old_code must exactly exist in the source.
4. old_code must appear exactly once.
5. new_code must be valid code for the target language.
6. Do not rewrite unrelated code.
7. Do not return shell commands.
8. Do not return markdown.
9. Return JSON only.
10. Preserve the existing coding style.
11. Do not invent files.
12. Only modify the specified target file.
"""

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        raw = response.output_text.strip()

        if raw.startswith("```"):

            raw = raw.replace(
                "```json",
                ""
            )

            raw = raw.replace(
                "```",
                ""
            )

            raw = raw.strip()

        return json.loads(raw)
