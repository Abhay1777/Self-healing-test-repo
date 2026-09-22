from pathlib import Path
from dotenv import load_dotenv

from agents.test_agent import TestAgent
from agents.debug_agent import DebugAgent


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO = PROJECT_ROOT / "test-repo"

load_dotenv(PROJECT_ROOT / ".env")


print("\n========== AGENT 2 ==========")
print("AI DEBUG AGENT")
print("==============================")

# Agent 1
tester = TestAgent(str(REPO))
result = tester.run_tests()

print("\nAgent 1 detected failure:")
print(result["output"])

# Read source code
source_file = REPO / "app.py"
source_code = source_file.read_text()

# Agent 2
debugger = DebugAgent()

patch = debugger.diagnose(
    source_code,
    result["output"]
)

print("\n========== AI DIAGNOSIS ==========")
print("Diagnosis:")
print(patch["diagnosis"])

print("\nFile:", patch["file"])
print("Line:", patch["line"])

print("\nOld code:")
print(patch["old_code"])

print("\nNew code:")
print(patch["new_code"])

print("\nReason:")
print(patch["reason"])

print("===================================")
