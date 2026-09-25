import os
import sys
import threading
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(ROOT / ".env")


from core.git_manager import GitManager
from core.healing_engine import HealingEngine


app = FastAPI(
    title="Self-Heal Git",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


STATE = {
    "running": False,
    "success": None,
    "attempts": 0,
    "trace": [],
    "error": None,
    "repository": None,
    "diff": "",
    "started_at": None,
    "completed_at": None,
    "committed": False,
    "commit_sha": None,
}


class HealRequest(BaseModel):
    repo_url: str
    commit_to_github: bool = False
    commit_message: str = (
        "fix: automatically repair failing tests"
    )


def add_trace(message, status="info"):
    STATE["trace"].append(
        {
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
    )


def run_repository_healing(
    repo_url,
    commit_to_github=False,
    commit_message="fix: automatically repair failing tests",
):
    git_manager = GitManager()

    workspace = None
    repo_path = None

    STATE.update(
        {
            "running": True,
            "success": None,
            "attempts": 0,
            "trace": [],
            "error": None,
            "repository": repo_url,
            "diff": "",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "committed": False,
            "commit_sha": None,
        }
    )

    try:
        add_trace(
            "Cloning GitHub repository"
        )

        repo_path, workspace = git_manager.clone(
            repo_url
        )

        add_trace(
            "Repository cloned successfully",
            "success",
        )

        add_trace(
            "Repository workspace created"
        )

        add_trace(
            "Starting autonomous healing engine"
        )

        engine = HealingEngine(
            repo_path
        )

        add_trace(
            "Starting autonomous healing pipeline"
        )

        result = engine.heal(
            max_attempts=3
        )

        STATE["attempts"] = result.get(
            "attempts",
            0,
        )

        for event in result.get(
            "trace",
            [],
        ):
            if isinstance(event, dict):
                STATE["trace"].append(event)
            else:
                STATE["trace"].append(
                    {
                        "message": str(event),
                        "status": "info",
                    }
                )

        STATE["diff"] = (
            git_manager.get_diff(
                repo_path
            )
        )

        if not result.get("success"):
            STATE["success"] = False

            error = result.get(
                "error",
                "Healing failed.",
            )

            STATE["error"] = error

            add_trace(
                f"Healing failed: {error}",
                "error",
            )

            return

        # IMPORTANT:
        # Only commit after verification succeeds.
        if commit_to_github:

            add_trace(
                "Verification passed - preparing GitHub commit",
                "success",
            )

            try:
                commit_result = (
                    git_manager.commit_and_push(
                        repo_path,
                        commit_message,
                    )
                )

                if commit_result["committed"]:

                    STATE["committed"] = True

                    STATE["commit_sha"] = (
                        commit_result["sha"]
                    )

                    add_trace(
                        "Changes committed to GitHub",
                        "success",
                    )

                    add_trace(
                        "Commit SHA: "
                        + commit_result["sha"],
                        "success",
                    )

                    add_trace(
                        "GitHub push completed successfully",
                        "success",
                    )

                else:

                    add_trace(
                        commit_result["message"],
                        "info",
                    )

            except Exception as commit_error:

                STATE["success"] = False

                STATE["error"] = (
                    "Healing succeeded, but GitHub commit failed: "
                    + str(commit_error)
                )

                add_trace(
                    "GitHub commit failed: "
                    + str(commit_error),
                    "error",
                )

                return

        add_trace(
            "Git repository successfully healed",
            "success",
        )

        STATE["success"] = True

    except Exception as error:

        STATE["success"] = False
        STATE["error"] = str(error)

        add_trace(
            str(error),
            "error",
        )

    finally:

        STATE["running"] = False
        STATE["completed_at"] = (
            datetime.now().isoformat()
        )

        if workspace:
            import shutil

            shutil.rmtree(
                workspace,
                ignore_errors=True,
            )


@app.get("/")
def root():
    return {
        "name": "Self-Heal Git",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/status")
def status():
    return STATE


@app.post("/heal-repository")
def heal_repository(request: HealRequest):

    if STATE["running"]:
        raise HTTPException(
            status_code=409,
            detail="A healing operation is already running.",
        )

    if not request.repo_url.strip():
        raise HTTPException(
            status_code=400,
            detail="Repository URL is required.",
        )

    thread = threading.Thread(
        target=run_repository_healing,
        args=(
            request.repo_url.strip(),
            request.commit_to_github,
            request.commit_message.strip()
            or "fix: automatically repair failing tests",
        ),
        daemon=True,
    )

    thread.start()

    return {
        "accepted": True,
        "message": (
            "Repository healing started."
        ),
        "repository": request.repo_url,
        "commit_to_github": request.commit_to_github,
    }


@app.post("/heal-demo")
def heal_demo():
    return {
        "message": "Use the frontend presentation demo."
    }
