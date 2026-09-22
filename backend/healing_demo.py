from pathlib import Path
from dotenv import load_dotenv

from core.healing_engine import HealingEngine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO = PROJECT_ROOT / "test-repo"

load_dotenv(PROJECT_ROOT / ".env")


print()
print("==============================================")
print("       SELF-HEAL GIT - AUTONOMOUS ENGINE")
print("==============================================")

print()
print("Repository:")
print(REPO)

print()
print("Starting healing process...")

engine = HealingEngine(str(REPO))

result = engine.heal(max_attempts=3)


print()
print("=============== HEALING TRACE ===============")

for step in result["trace"]:

    status = step["status"].upper()

    print(
        f"[{status}] "
        f"{step['agent']}: "
        f"{step['message']}"
    )


print()
print("==============================================")

if result["success"]:

    print("HEALING SUCCESSFUL")
    print(f"Attempts: {result['attempts']}")

else:

    print("HEALING FAILED")
    print(f"Attempts: {result['attempts']}")

print("==============================================")
