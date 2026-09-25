import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


class GitManager:

    def _get_token(self):
        load_dotenv(ENV_FILE, override=True)

        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise RuntimeError(
                "GITHUB_TOKEN is missing from .env"
            )

        return token.strip()

    def validate_url(self, repo_url):
        parsed = urlparse(repo_url)

        if parsed.scheme not in ["https", "http"]:
            raise ValueError(
                "Only HTTP/HTTPS Git repositories are supported."
            )

        if "github.com" not in parsed.netloc.lower():
            raise ValueError(
                "For this MVP, only GitHub repositories are supported."
            )

        path = parsed.path.rstrip("/")
        parts = path.split("/")

        if "tree" in parts:
            path = "/".join(parts[:parts.index("tree")])

        if "blob" in parts:
            path = "/".join(parts[:parts.index("blob")])

        if not path.endswith(".git"):
            path += ".git"

        return f"https://github.com{path}"

    def clone(self, repo_url):
        clean_url = self.validate_url(repo_url)

        workspace = Path(
            tempfile.mkdtemp(
                prefix="self_heal_git_"
            )
        )

        target = workspace / "repository"

        try:
            process = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    clean_url,
                    str(target),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if process.returncode != 0:
                error = (
                    process.stderr.strip()
                    or process.stdout.strip()
                    or "Git clone failed."
                )

                shutil.rmtree(
                    workspace,
                    ignore_errors=True,
                )

                raise RuntimeError(error)

            return target, workspace

        except Exception:
            shutil.rmtree(
                workspace,
                ignore_errors=True,
            )
            raise

    def get_diff(self, repo_path):
        process = subprocess.run(
            ["git", "diff"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return process.stdout

    def get_status(self, repo_path):
        process = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return process.stdout

    def has_changes(self, repo_path):
        return bool(
            self.get_status(repo_path).strip()
        )

    def _push_with_token(self, repo_path, remote_url):
        token = self._get_token()

        askpass_dir = Path(
            tempfile.mkdtemp(
                prefix="self_heal_askpass_"
            )
        )

        askpass_file = askpass_dir / "askpass.cmd"

        try:
            # Git Credential Manager is bypassed.
            # The token is supplied only through the temporary
            # askpass process and is never embedded in the URL.
            askpass_file.write_text(
                "@echo off\n"
                "if /I \"%~1\"==\"Username for 'https://github.com':\" "
                "echo x-access-token\n"
                "if /I \"%~1\"==\"Password for 'https://x-access-token@github.com':\" "
                "echo %GITHUB_TOKEN%\n"
                "if /I not \"%~1\"==\"Username for 'https://github.com':\" "
                "if /I not \"%~1\"==\"Password for 'https://x-access-token@github.com':\" "
                "echo %GITHUB_TOKEN%\n",
                encoding="utf-8",
            )

            env = os.environ.copy()

            env["GITHUB_TOKEN"] = token
            env["GIT_ASKPASS"] = str(askpass_file)
            env["GIT_TERMINAL_PROMPT"] = "0"

            process = subprocess.run(
                [
                    "git",
                    "-c",
                    "credential.helper=",
                    "push",
                    remote_url,
                    "HEAD:main",
                ],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )

            if process.returncode != 0:
                error = (
                    process.stderr.strip()
                    or process.stdout.strip()
                    or "Git push failed."
                )

                raise RuntimeError(error)

        finally:
            shutil.rmtree(
                askpass_dir,
                ignore_errors=True,
            )

    def commit_and_push(
        self,
        repo_path,
        commit_message,
    ):
        self._get_token()

        status = self.get_status(repo_path)

        if not status.strip():
            return {
                "committed": False,
                "message": "No changes to commit.",
                "sha": None,
            }

        # Configure Git identity
        subprocess.run(
            [
                "git",
                "config",
                "user.name",
                "Self-Heal Git",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            [
                "git",
                "config",
                "user.email",
                "self-heal-git@users.noreply.github.com",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Stage
        add_process = subprocess.run(
            [
                "git",
                "add",
                ".",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if add_process.returncode != 0:
            raise RuntimeError(
                add_process.stderr.strip()
                or "git add failed."
            )

        # Commit
        commit_process = subprocess.run(
            [
                "git",
                "commit",
                "-m",
                commit_message,
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if commit_process.returncode != 0:
            raise RuntimeError(
                commit_process.stderr.strip()
                or "git commit failed."
            )

        # SHA
        sha_process = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if sha_process.returncode != 0:
            raise RuntimeError(
                "Could not determine commit SHA."
            )

        sha = sha_process.stdout.strip()

        # Remote
        remote_process = subprocess.run(
            [
                "git",
                "remote",
                "get-url",
                "origin",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if remote_process.returncode != 0:
            raise RuntimeError(
                remote_process.stderr.strip()
                or "Could not read GitHub remote."
            )

        remote_url = remote_process.stdout.strip()

        # Push
        self._push_with_token(
            repo_path,
            remote_url,
        )

        return {
            "committed": True,
            "message": "Changes committed and pushed to GitHub.",
            "sha": sha,
        }