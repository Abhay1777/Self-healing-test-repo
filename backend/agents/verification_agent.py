from .test_agent import TestAgent


class VerificationAgent:

    def __init__(self, repo_path):

        self.test_agent = TestAgent(
            repo_path
        )


    def verify(self):

        result = self.test_agent.run_tests()

        return {
            "verified": result["passed"],
            "exit_code": result["exit_code"],
            "output": result["output"],
            "project_type": result.get(
                "project_type"
            ),
            "command": result.get(
                "command"
            )
        }
