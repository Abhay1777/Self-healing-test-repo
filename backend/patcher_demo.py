from pathlib import Path

from core.patcher import apply_patch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO = PROJECT_ROOT / "test-repo"


patch = {
    "file": "app.py",
    "line": 8,
    "old_code": "    return numbers[len(numbers)]",
    "new_code": "    return numbers[-2]"
}


print("\n========== PATCHER ==========")
print("Applying AI-generated patch...")
print("==============================")

result = apply_patch(
    REPO,
    patch
)

print("\nPatch applied successfully!")

print("\nFile:")
print(result["file"])

print("\nBefore:")
print(result["old_code"])

print("\nAfter:")
print(result["new_code"])

print("==============================")
