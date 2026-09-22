from pathlib import Path
import re


def extract_failure_info(test_output):

    # Python traceback:
    # File "app.py", line 8
    python_match = re.findall(
        r'File ["'']([^"'']+\.py)["''], line (\d+)',
        test_output
    )

    if python_match:

        file_path, line_number = python_match[-1]

        return {
            "file": file_path.replace("\\", "/"),
            "line": int(line_number)
        }

    # Pytest:
    # test_app.py:8
    pytest_match = re.findall(
        r'([A-Za-z0-9_./\\-]+\.py):(\d+)',
        test_output
    )

    if pytest_match:

        file_path, line_number = pytest_match[-1]

        return {
            "file": file_path.replace("\\", "/"),
            "line": int(line_number)
        }

    # ESLint / TypeScript / JavaScript:
    # src/app.jsx
    # 12:5
    eslint_match = re.findall(
        r'([A-Za-z0-9_./\\@\-]+\.(?:js|jsx|ts|tsx|mjs|cjs))'
        r'(?::(\d+)(?::\d+)?)',
        test_output
    )

    if eslint_match:

        file_path, line_number = eslint_match[-1]

        return {
            "file": file_path.replace("\\", "/"),
            "line": int(line_number)
        }

    # Generic source file followed by line/column.
    generic_match = re.findall(
        r'([A-Za-z0-9_./\\@\-]+\.(?:java|js|jsx|ts|tsx|py))'
        r'[:(](\d+)',
        test_output
    )

    if generic_match:

        file_path, line_number = generic_match[-1]

        return {
            "file": file_path.replace("\\", "/"),
            "line": int(line_number)
        }

    return None
