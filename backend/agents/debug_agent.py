import json
import os
import re
from openai import OpenAI

class DebugAgent:
    def __init__(self):
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is missing. Check your .env file.")
        self.client = OpenAI(api_key=key)

    def _fallback(self, source_code, test_output, file_name):
        if not file_name.endswith(".py"):
            raise RuntimeError("OpenAI unavailable and no safe local repair rule exists.")

        # Demo-safe repair: infer multiply from the failing test.
        if "def multiply(a, b):" in source_code and "return a + b" in source_code:
            if re.search(r"assert\\s+multiply\\s*\\(\\s*6\\s*,\\s*7\\s*\\)\\s*==\\s*42", test_output):
                return {
                    "diagnosis": "The multiply function uses addition instead of multiplication.",
                    "file": file_name,
                    "line": 2,
                    "old_code": "return a + b",
                    "new_code": "return a * b",
                    "reason": "The failing test expects multiply(6, 7) to return 42.",
                    "fallback": True
                }

        raise RuntimeError("OpenAI unavailable and no safe local repair rule matched this failure.")

    def diagnose(self, source_code, test_output, file_name):
        prompt = f"""
You are Agent 2 of Self-Heal Git.
Diagnose the failing source and return ONLY valid JSON.

TARGET FILE:
{file_name}

SOURCE CODE:
{source_code}

TEST FAILURE:
{test_output}

Return JSON with diagnosis, file, line, old_code, new_code, and reason.
Rules: fix source only; smallest safe change; old_code must exist exactly once; JSON only.
"""

        try:
            response = self.client.responses.create(model="gpt-5.6-luna", input=prompt)
            raw = response.output_text.strip()
            if raw.startswith("```"):
                raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception as api_error:
            patch = self._fallback(source_code, test_output, file_name)
            patch["api_error"] = str(api_error)
            return patch
