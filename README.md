# 🛠️ Self-Heal Git

### Autonomous Software Healing System

Self-Heal Git is an AI-powered system that automatically detects, diagnoses, and repairs software defects. It is designed to reduce the repetitive manual process of reading test failures, locating bugs, implementing fixes, and rerunning tests.

## 🎯 Problem We Solved

When a software project has failing tests, developers typically need to:

1. Read and understand the test failure.
2. Locate the problematic code.
3. Identify the root cause.
4. Implement a fix manually.
5. Run the tests again.
6. Repeat the process if the fix fails.
7. Commit the verified changes.

**Self-Heal Git automates this entire feedback loop.**

## ⚡ How We Solve It

```text
GitHub Repository
       ↓
Clone Repository
       ↓
Detect Project Type
       ↓
Run Tests
       ↓
Detect Failure
       ↓
Analyze Root Cause
       ↓
Generate Safe Patch
       ↓
Apply Patch
       ↓
Run Verification
       ↓
Tests Pass?
   ↓       ↓
  No      Yes
  ↓        ↓
Retry   Git Commit
           ↓
       GitHub Push
```

### 🔍 1. Automatic Failure Detection

The system automatically runs the project's tests and captures failures, error messages, and test output.

### 🤖 2. Root-Cause Analysis

The Debug Agent analyzes the failure and identifies the likely source of the defect.

### 🩹 3. Automatic Code Repair

A structured patch is generated for the affected code. The Safe Patcher validates the proposed change before applying it.

### 🧪 4. Automatic Verification

After repairing the code, the system reruns the tests. A fix is considered successful only when verification passes.

### 🔄 5. Autonomous Retry

If the generated fix does not resolve the problem, the system can retry the healing process.

### 🚀 6. GitHub Integration

After successful verification, the user can choose **"MAKE CHANGES IN YOUR REPO"** to automatically commit and push the verified repair back to GitHub.

### 📊 7. Transparent Execution

The React dashboard shows the complete healing process, including test failures, diagnosis, patching, verification, Git diff, and GitHub commit status.

## 🧪 Example

Suppose a repository contains:

```python
def multiply(a, b):
    return a + b
```

But the test expects:

```python
def test_multiply():
    assert multiply(6, 7) == 42
```

Self-Heal Git detects:

```text
Expected: 42
Actual:   13
```

The Debug Agent identifies that the function is using `+` instead of `*` and generates the repair:

```python
def multiply(a, b):
    return a * b
```

The system then reruns the tests:

```text
❌ Before: Tests Failed
✅ After:  Tests Passed
```

The verified change can then be committed and pushed back to GitHub.

## ✨ Key Features

* 🔍 Automated test failure detection
* 🤖 AI-powered debugging
* 🩹 Structured code patch generation
* 🛡️ Safe patch validation
* 🧪 Automated verification
* 🔄 Autonomous retry mechanism
* 📊 Real-time execution trace
* 🔀 Git diff generation
* 🚀 Optional GitHub commit & push

## 🛠️ Tech Stack

**Frontend:** React, Vite, JavaScript, CSS
**Backend:** Python, FastAPI
**AI:** OpenAI API
**Testing:** Pytest
**Version Control:** Git & GitHub

## ⚙️ Run Locally

### Backend

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Create a `.env` file containing your API credentials:

```env
OPENAI_API_KEY=your_key
GITHUB_TOKEN=your_token
```

>
## 👨‍💻 Author

**Abhay Dubey**
B.E. Information Technology — TCET

[GitHub](https://github.com/Abhay1777)
