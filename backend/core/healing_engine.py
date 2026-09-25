from pathlib import Path

from agents.test_agent import TestAgent
from agents.debug_agent import DebugAgent
from agents.verification_agent import VerificationAgent
from core.failure_parser import extract_failure_info
from core.patcher import apply_patch


class HealingEngine:

    def __init__(self, repo_path):
        self.repo_path = Path(repo_path).resolve()

        self.test_agent = TestAgent(str(self.repo_path))
        self.debug_agent = DebugAgent()
        self.verification_agent = VerificationAgent(str(self.repo_path))

        self.trace = []

    def log(self, agent, message, status="info"):
        self.trace.append({
            "agent": agent,
            "message": message,
            "status": status
        })

    def _find_source_file(self, failing_file):
        """
        If pytest points to a test file, inspect its imports and locate
        the actual application source file being tested.
        """

        test_file = self.repo_path / failing_file

        if not test_file.exists():
            return test_file

        try:
            content = test_file.read_text(encoding="utf-8-sig")
        except Exception:
            return test_file

        # Example:
        # from app import multiply
        for line in content.splitlines():

            stripped = line.strip()

            if stripped.startswith("from ") and " import " in stripped:
                module = (
                    stripped
                    .split("from ", 1)[1]
                    .split(" import ", 1)[0]
                    .strip()
                )

                candidate = self.repo_path / (module.replace(".", "/") + ".py")

                if candidate.exists():
                    return candidate

            # Example:
            # import app
            if stripped.startswith("import "):
                module = stripped.split("import ", 1)[1].split(",")[0].strip()

                candidate = self.repo_path / (
                    module.replace(".", "/") + ".py"
                )

                if candidate.exists():
                    return candidate

        return test_file

    def heal(self, max_attempts=3):

        self.trace = []

        self.log(
            "SYSTEM",
            "Starting autonomous healing pipeline"
        )

        project = self.test_agent.detect_project()

        self.log(
            "SYSTEM",
            f"Detected project type: {project['type']}"
        )

        if project.get("command"):
            self.log(
                "SYSTEM",
                "Test command: " + " ".join(project["command"])
            )
        else:
            self.log(
                "SYSTEM",
                "No automated test/build command detected"
            )

        for attempt in range(1, max_attempts + 1):

            self.log(
                "AGENT 1",
                f"Running tests - attempt {attempt}"
            )

            test_result = self.test_agent.run_tests()

            if test_result["passed"]:

                self.log(
                    "AGENT 1",
                    "Repository checks passed. No healing required.",
                    "success"
                )

                return {
                    "success": True,
                    "healed": False,
                    "healthy": True,
                    "attempts": attempt,
                    "project_type": test_result["project_type"],
                    "trace": self.trace
                }

            self.log(
                "AGENT 1",
                "Tests/checks failed",
                "error"
            )

            failure = extract_failure_info(
                test_result["output"]
            )

            if not failure:

                self.log(
                    "SYSTEM",
                    "Tests failed, but the failing source file could not be identified.",
                    "error"
                )

                return {
                    "success": False,
                    "healed": False,
                    "healthy": False,
                    "attempts": attempt,
                    "project_type": test_result["project_type"],
                    "trace": self.trace
                }

            failing_file = failure["file"]

            failing_path = (
                self.repo_path / failing_file
            )

            if not failing_path.exists():

                self.log(
                    "SYSTEM",
                    f"Failing file not found: {failing_file}",
                    "error"
                )

                return {
                    "success": False,
                    "healed": False,
                    "healthy": False,
                    "attempts": attempt,
                    "trace": self.trace
                }

            self.log(
                "SYSTEM",
                f"Failure located in {failing_file}:{failure['line']}"
            )

            # Read the actual failing test source.
            failing_source = failing_path.read_text(
                encoding="utf-8-sig"
            )

            # Locate the implementation file imported by the test.
            source_path = self._find_source_file(
                failing_file
            )

            source_code = source_path.read_text(
                encoding="utf-8-sig"
            )

            target_file = str(
                source_path.relative_to(self.repo_path)
            ).replace("\\", "/")

            # Give Agent 2 both:
            # 1. actual implementation source
            # 2. failing test source
            # 3. pytest output
            diagnostic_context = (
                test_result["output"]
                + "\n\n===== FAILING TEST SOURCE =====\n"
                + failing_source
            )

            self.log(
                "AGENT 2",
                "Analyzing failure and generating safe patch"
            )

            try:

                patch = self.debug_agent.diagnose(
                    source_code,
                    diagnostic_context,
                    target_file
                )

            except Exception as error:

                self.log(
                    "AGENT 2",
                    f"Diagnosis failed: {error}",
                    "error"
                )

                return {
                    "success": False,
                    "healed": False,
                    "healthy": False,
                    "attempts": attempt,
                    "project_type": test_result["project_type"],
                    "trace": self.trace
                }

            self.log(
                "AGENT 2",
                patch["diagnosis"]
            )

            self.log(
                "AGENT 2",
                f"Proposed fix at {patch['file']}:{patch['line']}"
            )

            self.log(
                "PATCHER",
                "Validating AI-generated patch"
            )

            try:

                applied_patch = apply_patch(
                    self.repo_path,
                    patch
                )

                self.log(
                    "PATCHER",
                    f"Patch applied to {applied_patch['file']}",
                    "success"
                )

            except Exception as error:

                self.log(
                    "PATCHER",
                    f"Patch rejected: {error}",
                    "error"
                )

                return {
                    "success": False,
                    "healed": False,
                    "healthy": False,
                    "attempts": attempt,
                    "project_type": test_result["project_type"],
                    "trace": self.trace
                }

            self.log(
                "AGENT 3",
                "Running verification checks"
            )

            verification = (
                self.verification_agent.verify()
            )

            if verification["verified"]:

                self.log(
                    "AGENT 3",
                    "All checks passed - healing complete",
                    "success"
                )

                return {
                    "success": True,
                    "healed": True,
                    "healthy": True,
                    "attempts": attempt,
                    "project_type": test_result["project_type"],
                    "trace": self.trace
                }

            self.log(
                "AGENT 3",
                "Fix did not resolve all failures",
                "error"
            )

        self.log(
            "SYSTEM",
            "Healing failed after maximum attempts",
            "error"
        )

        return {
            "success": False,
            "healed": False,
            "healthy": False,
            "attempts": max_attempts,
            "trace": self.trace
        }
