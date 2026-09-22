import sys
from pathlib import Path

# Make backend/ available as a top-level module directory.
# This allows existing imports such as:
# from core.healing_engine import HealingEngine
# from agents.test_agent import TestAgent

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from threading import Thread
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.git_manager import GitManager


load_dotenv(ROOT / ".env")


app = FastAPI(
    title="Self-Heal Git",
    version="2.0.0",
    description="Autonomous AI-powered Git repository healing system"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
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
    "completed_at": None
}


git_manager = GitManager()


def log(message, status="info", agent="SYSTEM"):

    STATE["trace"].append({
        "agent": agent,
        "message": message,
        "status": status
    })


def run_repository_healing(repo_url):

    workspace = None

    try:

        from core.healing_engine import HealingEngine

        STATE["running"] = True
        STATE["success"] = None
        STATE["attempts"] = 0
        STATE["trace"] = []
        STATE["error"] = None
        STATE["diff"] = ""
        STATE["repository"] = repo_url
        STATE["started_at"] = datetime.now().isoformat()
        STATE["completed_at"] = None

        log(
            "Cloning GitHub repository",
            "info",
            "GIT"
        )

        repo_path, workspace = git_manager.clone(
            repo_url
        )

        log(
            "Repository cloned successfully",
            "success",
            "GIT"
        )

        log(
            f"Repository workspace created",
            "info",
            "GIT"
        )

        log(
            "Starting autonomous healing engine",
            "info",
            "SYSTEM"
        )

        engine = HealingEngine(
            str(repo_path)
        )

        result = engine.heal(
            max_attempts=3
        )

        STATE["success"] = result["success"]
        STATE["attempts"] = result["attempts"]

        STATE["trace"].extend(
            result["trace"]
        )

        STATE["diff"] = git_manager.get_diff(
            repo_path
        )

        if STATE["success"]:

            log(
                "Git repository successfully healed",
                "success",
                "GIT"
            )

        else:

            log(
                "Repository could not be healed",
                "error",
                "SYSTEM"
            )

    except Exception as error:

        STATE["success"] = False
        STATE["error"] = str(error)

        log(
            str(error),
            "error",
            "SYSTEM"
        )

    finally:

        if workspace:

            import shutil

            shutil.rmtree(
                workspace,
                ignore_errors=True
            )

        STATE["running"] = False
        STATE["completed_at"] = datetime.now().isoformat()


@app.get("/")
def root():

    return {
        "application": "Self-Heal Git",
        "version": "2.0.0",
        "status": "online"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "git_integration": True
    }


@app.get("/status")
def status():

    return STATE


@app.post("/heal-demo")
def heal_demo():

    if STATE["running"]:

        return {
            "accepted": False,
            "message": "Healing is already running."
        }

    repo = ROOT / "test-repo"

    from core.healing_engine import HealingEngine

    STATE["running"] = True
    STATE["success"] = None
    STATE["attempts"] = 0
    STATE["trace"] = []
    STATE["error"] = None
    STATE["diff"] = ""
    STATE["repository"] = "Local Demo"
    STATE["started_at"] = datetime.now().isoformat()
    STATE["completed_at"] = None

    def demo():

        try:

            engine = HealingEngine(
                str(repo)
            )

            result = engine.heal(
                max_attempts=3
            )

            STATE["success"] = result["success"]
            STATE["attempts"] = result["attempts"]
            STATE["trace"] = result["trace"]
            STATE["diff"] = git_manager.get_diff(repo)

        except Exception as error:

            STATE["success"] = False
            STATE["error"] = str(error)

        finally:

            STATE["running"] = False
            STATE["completed_at"] = datetime.now().isoformat()

    Thread(
        target=demo,
        daemon=True
    ).start()

    return {
        "accepted": True,
        "message": "Demo healing started."
    }


@app.post("/heal-repository")
def heal_repository(payload: dict):

    if STATE["running"]:

        return {
            "accepted": False,
            "message": "Healing is already running."
        }

    repo_url = payload.get(
        "repo_url",
        ""
    ).strip()

    if not repo_url:

        return {
            "accepted": False,
            "message": "GitHub repository URL is required."
        }

    try:

        git_manager.validate_url(
            repo_url
        )

    except Exception as error:

        return {
            "accepted": False,
            "message": str(error)
        }

    Thread(
        target=run_repository_healing,
        args=(repo_url,),
        daemon=True
    ).start()

    return {
        "accepted": True,
        "message": "Repository healing started.",
        "repository": repo_url
    }
