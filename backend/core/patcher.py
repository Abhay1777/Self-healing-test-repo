from pathlib import Path
import ast


def apply_patch(repo_path, patch):

    repo_path = Path(
        repo_path
    ).resolve()

    file_path = (
        repo_path /
        patch["file"]
    ).resolve()

    # Security: patch must remain inside repository.
    try:

        file_path.relative_to(
            repo_path
        )

    except ValueError:

        raise ValueError(
            "Patch rejected: target file is outside repository."
        )

    if not file_path.exists():

        raise FileNotFoundError(
            f"Target file not found: {file_path}"
        )

    source = file_path.read_text(
        encoding="utf-8-sig"
    )

    old_code = patch["old_code"]
    new_code = patch["new_code"]

    if not old_code:

        raise ValueError(
            "Patch rejected: old_code is empty."
        )

    if old_code not in source:

        raise ValueError(
            "Patch rejected: old_code was not found in source."
        )

    occurrences = source.count(
        old_code
    )

    if occurrences != 1:

        raise ValueError(
            f"Patch rejected: old_code appears "
            f"{occurrences} times. Expected exactly once."
        )

    updated_source = source.replace(
        old_code,
        new_code,
        1
    )

    updated_source = updated_source.lstrip(
        "\ufeff"
    )

    extension = file_path.suffix.lower()

    # Python syntax validation.
    if extension == ".py":

        try:

            ast.parse(
                updated_source
            )

        except SyntaxError as error:

            raise ValueError(
                "Patch rejected: generated Python "
                f"code has invalid syntax: {error}"
            )

    # JavaScript syntax validation for normal JS files.
    # JSX/TSX syntax is verified by the project's
    # lint/build command instead.
    if extension in [
        ".js",
        ".mjs",
        ".cjs"
    ]:

        import subprocess

        try:

            process = subprocess.run(
                [
                    "node",
                    "--check"
                ],
                input=updated_source,
                capture_output=True,
                text=True,
                timeout=30
            )

            if process.returncode != 0:

                raise ValueError(
                    "Patch rejected: generated JavaScript "
                    "has invalid syntax.\n"
                    + process.stderr
                )

        except FileNotFoundError:

            pass

    file_path.write_text(
        updated_source,
        encoding="utf-8"
    )

    return {
        "file": patch["file"],
        "old_code": old_code,
        "new_code": new_code
    }
