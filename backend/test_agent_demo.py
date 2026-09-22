from pathlib import Path

from agents.test_agent import TestAgent


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO = PROJECT_ROOT / "test-repo"


agent = TestAgent(str(REPO))

result = agent.run_tests()


print("\n========== SELF-HEAL GIT ==========")
print("AGENT 1 - TEST AGENT")
print("===================================")

print("Repository:", REPO)
print("Tests passed:", result["passed"])
print("Exit code:", result["exit_code"])

print("\n---------- TEST OUTPUT ----------")
print(result["output"])
print("=================================\n")
