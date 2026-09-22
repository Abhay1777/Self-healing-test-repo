from pathlib import Path

from agents.verification_agent import VerificationAgent


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO = PROJECT_ROOT / "test-repo"


print("\n========== AGENT 3 ==========")
print("VERIFICATION AGENT")
print("==============================")

agent = VerificationAgent(str(REPO))

result = agent.verify()

print("\nVerification result:")
print("Tests passed:", result["verified"])
print("Exit code:", result["exit_code"])

print("\n---------- TEST OUTPUT ----------")
print(result["output"])

if result["verified"]:
    print("\nHEALING VERIFIED")
else:
    print("\nHEALING FAILED")

print("================================")
