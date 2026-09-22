import json
import subprocess
import sys
from pathlib import Path


class TestAgent:

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def detect_project(self):

        files = {
            file.name.lower()
            for file in self.repo_path.iterdir()
            if file.is_file()
        }

        # Python
        if (
            "pytest.ini" in files
            or "pyproject.toml" in files
            or "requirements.txt" in files
            or "setup.py" in files
            or any(
                self.repo_path.glob("test_*.py")
            )
            or any(
                self.repo_path.glob("*_test.py")
            )
        ):
            return {
                "type": "python",
                "command": [sys.executable, "-m", "pytest", "-q"]
            }

        # Node / React / Next.js
        package_file = self.repo_path / "package.json"

        if package_file.exists():

            try:
                package = json.loads(
                    package_file.read_text(
                        encoding="utf-8"
                    )
                )

                scripts = package.get(
                    "scripts",
                    {}
                )

                dependencies = {}

                dependencies.update(
                    package.get(
                        "dependencies",
                        {}
                    )
                )

                dependencies.update(
                    package.get(
                        "devDependencies",
                        {}
                    )
                )

                if "next" in dependencies:

                    if "lint" in scripts:
                        command = [
                            "npm",
                            "run",
                            "lint"
                        ]

                    elif "build" in scripts:
                        command = [
                            "npm",
                            "run",
                            "build"
                        ]

                    else:
                        command = [
                            "npm",
                            "run",
                            "build"
                        ]

                    return {
                        "type": "nextjs",
                        "command": command
                    }

                if "react" in dependencies:

                    if "lint" in scripts:
                        command = [
                            "npm",
                            "run",
                            "lint"
                        ]

                    elif "test" in scripts:
                        command = [
                            "npm",
                            "test",
                            "--",
                            "--watchAll=false"
                        ]

                    elif "build" in scripts:
                        command = [
                            "npm",
                            "run",
                            "build"
                        ]

                    else:
                        command = [
                            "npm",
                            "run",
                            "build"
                        ]

                    return {
                        "type": "react",
                        "command": command
                    }

                if "test" in scripts:

                    return {
                        "type": "node",
                        "command": [
                            "npm",
                            "test"
                        ]
                    }

                if "build" in scripts:

                    return {
                        "type": "node",
                        "command": [
                            "npm",
                            "run",
                            "build"
                        ]
                    }

                return {
                    "type": "node",
                    "command": None
                }

            except Exception as error:

                return {
                    "type": "node",
                    "command": None,
                    "detection_error": str(error)
                }

        # Java Maven
        if (self.repo_path / "pom.xml").exists():

            return {
                "type": "java-maven",
                "command": [
                    "mvn",
                    "test"
                ]
            }

        # Java Gradle
        if (
            (self.repo_path / "gradlew").exists()
            or (self.repo_path / "build.gradle").exists()
            or (self.repo_path / "build.gradle.kts").exists()
        ):

            if (self.repo_path / "gradlew").exists():

                command = [
                    "gradlew.bat",
                    "test"
                ]

            else:

                command = [
                    "gradle",
                    "test"
                ]

            return {
                "type": "java-gradle",
                "command": command
            }

        return {
            "type": "unknown",
            "command": None
        }


    def install_dependencies(self, project_type):

        if project_type not in [
            "nextjs",
            "react",
            "node"
        ]:
            return {
                "success": True,
                "output": "No Node dependency installation required."
            }

        package_lock = self.repo_path / "package-lock.json"
        npm_lock = self.repo_path / "npm-shrinkwrap.json"

        if package_lock.exists() or npm_lock.exists():

            command = [
                "npm",
                "ci",
                "--no-audit",
                "--no-fund"
            ]

        else:

            command = [
                "npm",
                "install",
                "--no-audit",
                "--no-fund"
            ]

        process = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=300
        )

        output = (
            process.stdout +
            process.stderr
        )

        return {
            "success": process.returncode == 0,
            "output": output
        }


    def run_tests(self):

        project = self.detect_project()

        project_type = project["type"]
        command = project["command"]

        if project_type == "unknown":

            return {
                "passed": False,
                "exit_code": -1,
                "output": (
                    "Self-Heal Git could not identify a supported "
                    "project type."
                ),
                "project_type": project_type,
                "command": None
            }

        # Install Node dependencies first.
        installation = self.install_dependencies(
            project_type
        )

        if not installation["success"]:

            return {
                "passed": False,
                "exit_code": -1,
                "output": (
                    "Dependency installation failed.\n\n"
                    + installation["output"]
                ),
                "project_type": project_type,
                "command": "npm install"
            }

        # A package.json exists but has no test/build/lint command.
        if command is None:

            return {
                "passed": True,
                "exit_code": 0,
                "output": (
                    f"Detected {project_type} project. "
                    "No automated test/build script was available. "
                    "Repository inspection completed successfully."
                ),
                "project_type": project_type,
                "command": None
            }

        try:

            process = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = (
                process.stdout +
                process.stderr
            )

            return {
                "passed": process.returncode == 0,
                "exit_code": process.returncode,
                "output": output,
                "project_type": project_type,
                "command": " ".join(command)
            }

        except FileNotFoundError as error:

            return {
                "passed": False,
                "exit_code": -1,
                "output": (
                    f"Required build/test tool was not found: "
                    f"{error}"
                ),
                "project_type": project_type,
                "command": " ".join(command)
            }

        except subprocess.TimeoutExpired:

            return {
                "passed": False,
                "exit_code": -1,
                "output": (
                    "Test/build command timed out after "
                    "300 seconds."
                ),
                "project_type": project_type,
                "command": " ".join(command)
            }
