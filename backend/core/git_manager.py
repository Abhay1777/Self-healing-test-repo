import subprocess
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urlparse


class GitManager:

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

        if not repo_url.endswith(".git"):
            repo_url = repo_url.rstrip("/") + ".git"

        return repo_url


    def clone(self, repo_url):

        repo_url = self.validate_url(repo_url)

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
                    repo_url,
                    str(target)
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            if process.returncode != 0:

                shutil.rmtree(
                    workspace,
                    ignore_errors=True
                )

                raise RuntimeError(
                    process.stderr.strip()
                )

            return target, workspace

        except Exception:

            shutil.rmtree(
                workspace,
                ignore_errors=True
            )

            raise


    def get_diff(self, repo_path):

        process = subprocess.run(
            [
                "git",
                "diff"
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        return process.stdout


    def get_status(self, repo_path):

        process = subprocess.run(
            [
                "git",
                "status",
                "--short"
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        return process.stdout
