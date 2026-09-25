import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import "./App.css";

const API = "http://127.0.0.1:8000";

const DEFAULT_REPO =
  "https://github.com/Abhay1777/Self-heal-test-repo-2";

const demoSteps = [
  {
    agent: "GIT",
    message: "Cloning GitHub repository",
    status: "info",
  },
  {
    agent: "GIT",
    message: "Repository cloned successfully",
    status: "success",
  },
  {
    agent: "SYSTEM",
    message: "Repository workspace created",
    status: "info",
  },
  {
    agent: "SYSTEM",
    message: "Starting autonomous healing pipeline",
    status: "info",
  },
  {
    agent: "SYSTEM",
    message: "Detected project type: Python",
    status: "success",
  },
  {
    agent: "TEST",
    message: "Running tests — attempt 1",
    status: "info",
  },
  {
    agent: "TEST",
    message: "2 tests passed, 1 test failed",
    status: "error",
  },
  {
    agent: "TEST",
    message: "Failure detected in app.py",
    status: "error",
  },
  {
    agent: "DEBUG",
    message: "Analyzing failure with AI Debug Agent",
    status: "info",
  },
  {
    agent: "DEBUG",
    message:
      "Root cause identified: incorrect second-largest index",
    status: "success",
  },
  {
    agent: "DEBUG",
    message: "Safe structured patch generated",
    status: "success",
  },
  {
    agent: "PATCH",
    message: "Validating patch against repository",
    status: "info",
  },
  {
    agent: "PATCH",
    message: "Patch applied successfully",
    status: "success",
  },
  {
    agent: "VERIFY",
    message: "Running verification tests",
    status: "info",
  },
  {
    agent: "VERIFY",
    message: "All tests passed",
    status: "success",
  },
  {
    agent: "SYSTEM",
    message: "HEALING VERIFIED",
    status: "success",
  },
];

const demoDiff = `--- a/app.py
+++ b/app.py
@@
 def get_second_largest(numbers):
     numbers = sorted(numbers)
-    return numbers[len(numbers)]
+    return numbers[-2]`;

function App() {
  /*
   * IMPORTANT:
   * This ref tells us whether the user has started a NEW
   * healing execution during the current page session.
   *
   * On a browser refresh it becomes false again, so the
   * previous backend result is NOT restored into the UI.
   */
  const hasStartedExecution = useRef(false);

  const [repoUrl, setRepoUrl] = useState(
    DEFAULT_REPO
  );

  const [status, setStatus] = useState({
    running: false,
    success: false,
    attempts: 0,
    trace: [],
    error: "",
    repository: "",
    diff: "",
    project_type: "",
    committed: false,
    commit_sha: null,
  });

  const [loading, setLoading] = useState(false);

  const [demoRunning, setDemoRunning] =
    useState(false);

  const [message, setMessage] = useState("");

  /*
   * GitHub write-back option
   */
  const [commitToGithub, setCommitToGithub] =
    useState(false);

  const [commitMessage, setCommitMessage] =
    useState(
      "fix: automatically repair failing tests"
    );

  /*
   * Poll the REAL backend.
   *
   * IMPORTANT:
   * We deliberately do NOT fetch the old /status result
   * when the page first loads.
   *
   * This prevents a previous successful run from showing
   * COMMITTED after a browser refresh.
   */
  useEffect(() => {
    let active = true;

    const loadStatus = async () => {
      /*
       * Do not restore an old backend run after refresh.
       */
      if (!hasStartedExecution.current) {
        return;
      }

      try {
        const res = await fetch(`${API}/status`);

        if (!res.ok) {
          return;
        }

        const data = await res.json();

        if (!active) {
          return;
        }

        setStatus(data);

        if (!data.running) {
          setLoading(false);
        }
      } catch {
        /*
         * Backend may temporarily be unavailable.
         */
      }
    };

    /*
     * We intentionally DO NOT call loadStatus()
     * immediately on page load.
     *
     * The interval will begin checking once the user
     * starts a new execution.
     */
    const interval = setInterval(
      loadStatus,
      1200
    );

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  /*
   * Convert trace into a predictable array.
   */
  const trace = useMemo(() => {
    if (!status?.trace) {
      return [];
    }

    if (Array.isArray(status.trace)) {
      return status.trace;
    }

    if (
      typeof status.trace === "object"
    ) {
      return Object.entries(
        status.trace
      ).map(([key, value]) => ({
        agent: "SYSTEM",
        message:
          typeof value === "string"
            ? value
            : `${key}: ${JSON.stringify(
                value
              )}`,
        status: "info",
      }));
    }

    return [];
  }, [status]);

  /*
   * Pipeline state.
   */
  const getStepState = (step) => {
    const text = trace
      .map((x) => JSON.stringify(x))
      .join(" ")
      .toLowerCase();

    /*
     * Presentation demo
     */
    if (demoRunning) {
      if (step === 1) {
        if (
          text.includes("tests") ||
          text.includes("test agent")
        ) {
          return "done";
        }

        return "running";
      }

      if (step === 2) {
        if (
          text.includes(
            "safe structured patch"
          ) ||
          text.includes("patch generated")
        ) {
          return "done";
        }

        if (
          text.includes("analyzing") ||
          text.includes("root cause")
        ) {
          return "running";
        }

        return "idle";
      }

      if (step === 3) {
        if (
          text.includes("patch applied")
        ) {
          return "done";
        }

        if (
          text.includes("validating patch")
        ) {
          return "running";
        }

        return "idle";
      }

      if (step === 4) {
        if (
          text.includes("healing verified")
        ) {
          return "done";
        }

        if (
          text.includes("verification")
        ) {
          return "running";
        }

        return "idle";
      }
    }

    /*
     * Real backend state
     */
    if (step === 1) {
      if (
        text.includes("tests/checks passed") ||
        text.includes("tests passed") ||
        text.includes("tests failed")
      ) {
        return "done";
      }

      if (loading) {
        return "running";
      }

      return "idle";
    }

    if (step === 2) {
      if (
        text.includes("debug") ||
        text.includes("diagnos") ||
        text.includes("patch")
      ) {
        return status.success
          ? "done"
          : loading
            ? "running"
            : "idle";
      }

      return "idle";
    }

    if (step === 3) {
      if (text.includes("patch")) {
        return status.success
          ? "done"
          : loading
            ? "running"
            : "idle";
      }

      return "idle";
    }

    if (step === 4) {
      if (
        text.includes("verif") ||
        text.includes("healing verified") ||
        status.success
      ) {
        return status.success
          ? "done"
          : loading
            ? "running"
            : "idle";
      }

      return "idle";
    }

    return "idle";
  };

  /*
   * REAL HEALING
   */
  const startHealing = async () => {
    if (!repoUrl.trim()) {
      setMessage(
        "Enter a GitHub repository URL."
      );
      return;
    }

    /*
     * Tell the polling effect that a NEW execution
     * has started.
     */
    hasStartedExecution.current = true;

    /*
     * Immediately clear the previous result.
     */
    setStatus({
      running: true,
      success: false,
      attempts: 0,
      trace: [],
      error: "",
      repository: repoUrl.trim(),
      diff: "",
      project_type: "",
      committed: false,
      commit_sha: null,
    });

    setLoading(true);
    setMessage("");

    try {
      const res = await fetch(
        `${API}/heal-repository`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            repo_url: repoUrl.trim(),

            /*
             * IMPORTANT:
             * Send the checkbox state to FastAPI.
             */
            commit_to_github:
              commitToGithub,

            commit_message:
              commitMessage.trim() ||
              "fix: automatically repair failing tests",
          }),
        }
      );

      const data = await res.json();

      if (!res.ok) {
        throw new Error(
          data.detail ||
            "Healing request failed."
        );
      }

      /*
       * Backend may return an initial state.
       * Polling will continue updating it.
       */
      setStatus(data);
    } catch (error) {
      setStatus((previous) => ({
        ...previous,
        running: false,
        success: false,
        error:
          error.message ||
          "Unable to start healing.",
      }));

      setMessage(
        error.message ||
          "Unable to start healing."
      );

      setLoading(false);
    }
  };

  /*
   * LOCAL PRESENTATION DEMO
   *
   * Does NOT call OpenAI.
   * Useful for presentation/video.
   */
  const runDemo = async () => {
    /*
     * This is a local demo, so don't use the backend
     * polling state.
     */
    hasStartedExecution.current = false;

    setDemoRunning(true);
    setLoading(false);
    setMessage("");

    setStatus({
      running: true,
      success: false,
      attempts: 1,
      trace: [],
      error: "",
      repository: repoUrl,
      diff: "",
      project_type: "Python",
      committed: false,
      commit_sha: null,
    });

    for (
      let i = 0;
      i < demoSteps.length;
      i++
    ) {
      await new Promise((resolve) =>
        setTimeout(resolve, 750)
      );

      const currentTrace =
        demoSteps.slice(0, i + 1);

      setStatus({
        running:
          i <
          demoSteps.length - 1,

        success:
          i ===
          demoSteps.length - 1,

        attempts: 1,

        trace: currentTrace,

        error: "",

        repository: repoUrl,

        diff:
          i ===
          demoSteps.length - 1
            ? demoDiff
            : "",

        project_type: "Python",

        committed: false,

        commit_sha: null,
      });
    }

    setDemoRunning(false);
  };

  const isBusy =
    loading || demoRunning;

  /*
   * Status label
   */
  let statusLabel = "READY";

  if (loading) {
    statusLabel = "HEALING";
  } else if (demoRunning) {
    statusLabel = "HEALING";
  } else if (status?.committed) {
    statusLabel = "COMMITTED";
  } else if (status?.success) {
    statusLabel = "HEALED";
  } else if (status?.error) {
    statusLabel = "ERROR";
  } else if (
    trace.some((x) =>
      String(x.message || "")
        .toLowerCase()
        .includes(
          "passed. no healing required"
        )
    )
  ) {
    statusLabel = "HEALTHY";
  }

  const systemOnline = true;

  return (
    <div className="app">

      {/* TOP BAR */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-logo">
            SH
          </div>

          <div>

            <div className="brand-name">
              SELF-HEAL GIT
            </div>

            <div className="brand-subtitle">
              Autonomous Software Healing
            </div>

          </div>

        </div>

        <div className="system-status">

          <span className="status-dot online" />

          {systemOnline
            ? "SYSTEM ONLINE"
            : "BACKEND OFFLINE"}

        </div>

      </header>


      <main className="container">

        {/* HERO */}

        <section className="hero">

          <div className="hero-copy">

            <div className="eyebrow">
              AUTONOMOUS DEVELOPER INFRASTRUCTURE
            </div>

            <h1>
              Detect.
              <br />
              <span>Diagnose.</span>
              <br />
              Heal.
            </h1>

            <p>
              Self-Heal Git automatically detects
              software failures, diagnoses the root
              cause with AI, applies a validated patch,
              verifies the result, and can commit the
              verified repair directly to GitHub.
            </p>

            <div className="hero-tags">

              <span>AI DEBUGGING</span>

              <span>SAFE PATCHING</span>

              <span>AUTOMATED TESTING</span>

              <span>GITHUB WRITE-BACK</span>

            </div>

          </div>


          <div className="status-card">

            <div className="card-label">
              CURRENT STATUS
            </div>

            <div
              className={`big-status ${
                demoRunning || loading
                  ? "active"
                  : status?.committed
                    ? "success"
                    : status?.success
                      ? "success"
                      : status?.error
                        ? "error"
                        : ""
              }`}
            >
              {statusLabel}
            </div>

            <div className="status-divider" />

            <div className="stat-row">

              <span>ATTEMPTS</span>

              <strong>
                {status?.attempts ?? 0}
              </strong>

            </div>

            <div className="stat-row">

              <span>EVENTS</span>

              <strong>
                {trace.length}
              </strong>

            </div>

            <div className="stat-row">

              <span>PROJECT</span>

              <strong>
                {status?.project_type || "—"}
              </strong>

            </div>

            {status?.committed && (
              <div
                className="github-success-indicator"
                style={{
                  marginTop: "18px",
                  padding: "12px",
                  border:
                    "1px solid rgba(60, 220, 160, 0.35)",
                  borderRadius: "6px",
                  color: "#48e6a3",
                  fontFamily:
                    "DM Mono, monospace",
                  fontSize: "9px",
                  letterSpacing: "0.08em",
                  textAlign: "center",
                  background:
                    "rgba(30, 150, 100, 0.08)",
                }}
              >
                ✓ GITHUB UPDATED
              </div>
            )}

          </div>

        </section>


        {/* REPOSITORY */}

        <section className="repo-card">

          <div className="section-eyebrow">
            GITHUB REPOSITORY
          </div>

          <h2>
            Heal a real repository
          </h2>

          <p className="repo-description">
            Connect a repository and let the
            autonomous healing pipeline inspect,
            diagnose, patch, verify and optionally
            commit the repair back to GitHub.
          </p>


          <div className="repo-input-row">

            <div className="input-wrapper">

              <span className="github-icon">
                ◉
              </span>

              <input
                value={repoUrl}
                onChange={(e) =>
                  setRepoUrl(
                    e.target.value
                  )
                }
                placeholder="https://github.com/username/repository"
                disabled={isBusy}
              />

            </div>


            <button
              className="heal-button"
              onClick={startHealing}
              disabled={isBusy}
            >

              {loading ? (
                <>
                  <span className="spinner" />
                  HEALING...
                </>
              ) : (
                <>
                  ANALYZE & HEAL
                  <span>→</span>
                </>
              )}

            </button>

          </div>


          {/* GITHUB WRITE-BACK OPTION */}

          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
              marginTop: "16px",
              padding: "15px 18px",
              border:
                "1px solid rgba(255,255,255,0.10)",
              borderRadius: "7px",
              cursor: isBusy
                ? "not-allowed"
                : "pointer",
              opacity: isBusy ? 0.6 : 1,
              background:
                "rgba(255,255,255,0.015)",
            }}
          >

            <input
              type="checkbox"
              checked={commitToGithub}
              disabled={isBusy}
              onChange={(e) =>
                setCommitToGithub(
                  e.target.checked
                )
              }
              style={{
                width: "18px",
                height: "18px",
                accentColor: "#48e6a3",
                cursor: "pointer",
              }}
            />

            <div
              style={{
                flex: 1,
              }}
            >

              <div
                style={{
                  fontFamily:
                    "DM Mono, monospace",
                  fontSize: "10px",
                  fontWeight: 700,
                  letterSpacing:
                    "0.08em",
                  color: "#ffffff",
                }}
              >
                MAKE CHANGES IN YOUR REPO
              </div>

              <div
                style={{
                  marginTop: "5px",
                  fontFamily:
                    "DM Mono, monospace",
                  fontSize: "8px",
                  letterSpacing:
                    "0.04em",
                  color: "#777",
                }}
              >
                After verification passes,
                automatically commit and push
                the fixed code to GitHub.
              </div>

            </div>

          </label>


          {/* COMMIT MESSAGE */}

          {commitToGithub && (
            <div
              style={{
                marginTop: "10px",
              }}
            >

              <input
                value={commitMessage}
                onChange={(e) =>
                  setCommitMessage(
                    e.target.value
                  )
                }
                disabled={isBusy}
                placeholder="Commit message"
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "12px 14px",
                  background:
                    "rgba(0,0,0,0.25)",
                  border:
                    "1px solid rgba(255,255,255,0.10)",
                  borderRadius: "6px",
                  color: "#fff",
                  outline: "none",
                  fontFamily:
                    "DM Mono, monospace",
                  fontSize: "9px",
                }}
              />

            </div>
          )}


          {/* COMMITTED MESSAGE */}

          {status?.committed && (
            <div
              style={{
                marginTop: "10px",
                padding: "14px 16px",
                border:
                  "1px solid rgba(60,220,160,0.35)",
                borderRadius: "7px",
                background:
                  "rgba(30,150,100,0.08)",
                color: "#48e6a3",
                fontFamily:
                  "DM Mono, monospace",
                fontSize: "9px",
                letterSpacing:
                  "0.06em",
              }}
            >
              ✓ FIX COMMITTED & PUSHED TO GITHUB

              {status.commit_sha && (
                <div
                  style={{
                    marginTop: "7px",
                    color: "#777",
                    fontSize: "8px",
                  }}
                >
                  COMMIT:{" "}
                  {status.commit_sha}
                </div>
              )}

            </div>
          )}


          {/* PRESENTATION DEMO */}

          <button
            className="demo-button"
            onClick={runDemo}
            disabled={isBusy}
          >
            {demoRunning
              ? "RUNNING DEMO..."
              : "▶ RUN PRESENTATION DEMO"}
          </button>


          {demoRunning && (
            <div
              style={{
                marginTop: "12px",
                color: "#777aff",
                fontFamily:
                  "DM Mono, monospace",
                fontSize: "8px",
                letterSpacing:
                  "0.08em",
              }}
            >
              DEMO MODE — LOCAL SIMULATION
            </div>
          )}


          {message && (
            <div className="error-message">
              {message}
            </div>
          )}

        </section>


        {/* PIPELINE */}

        <section className="pipeline-section">

          <div className="section-eyebrow">
            AUTONOMOUS PIPELINE
          </div>

          <h2>
            Healing Workflow
          </h2>


          <div className="pipeline">

            <PipelineStep
              number="01"
              title="TEST AGENT"
              description="Detect"
              state={getStepState(1)}
            />

            <PipelineArrow />

            <PipelineStep
              number="02"
              title="AI DEBUG"
              description="Diagnose"
              state={getStepState(2)}
            />

            <PipelineArrow />

            <PipelineStep
              number="03"
              title="SAFE PATCHER"
              description="Repair"
              state={getStepState(3)}
            />

            <PipelineArrow />

            <PipelineStep
              number="04"
              title="VERIFICATION"
              description="Verify"
              state={getStepState(4)}
            />

          </div>

        </section>


        {/* TRACE */}

        <section className="activity-section">

          <div className="section-eyebrow">
            EXECUTION TRACE
          </div>

          <h2>
            Agent Activity
          </h2>


          <div className="terminal">

            <div className="terminal-header">

              <div className="terminal-dots">
                <span />
                <span />
                <span />
              </div>

              <span>
                self-heal-engine
              </span>

              <span className="terminal-live">
                ● LIVE
              </span>

            </div>


            <div className="terminal-body">

              {trace.length === 0 ? (

                <div className="empty-terminal">

                  <span className="terminal-cursor">
                    _
                  </span>

                  Waiting for healing execution...

                </div>

              ) : (

                trace.map(
                  (item, index) => {

                    const text =
                      typeof item ===
                      "string"
                        ? item
                        : item?.message ||
                          item?.event ||
                          item?.step ||
                          JSON.stringify(
                            item
                          );

                    return (
                      <div
                        className="log-line"
                        key={index}
                      >

                        <span className="log-number">
                          {String(
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )}
                        </span>

                        <span className="log-symbol">
                          ›
                        </span>

                        <span>
                          {text}
                        </span>

                      </div>
                    );

                  }
                )

              )}

            </div>

          </div>

        </section>


        {/* RESULT */}

        {(status?.diff ||
          status?.success) && (

          <section className="result-section">

            <div className="section-eyebrow">
              RESULT
            </div>


            <div className="result-card">

              <div className="result-icon">
                ✓
              </div>


              <div>

                <div className="result-title">

                  {status?.committed
                    ? "FIX COMMITTED TO GITHUB"
                    : "HEALING VERIFIED"}

                </div>

                <div className="result-subtitle">

                  {status?.committed
                    ? "Repository repaired, verified and updated successfully."
                    : "Repository verification completed successfully."}

                </div>

              </div>


              <div className="result-badge">

                {status?.committed
                  ? "GITHUB UPDATED"
                  : "ALL TESTS PASSED"}

              </div>

            </div>


            {status?.diff && (

              <div className="diff-card">

                <div className="diff-header">

                  <span>
                    GENERATED GIT DIFF
                  </span>

                  <span className="diff-file">
                    PATCH
                  </span>

                </div>


                <pre>
                  {status.diff}
                </pre>

              </div>

            )}

          </section>

        )}


        <footer>

          <span>
            SELF-HEAL GIT
          </span>

          <span>
            AI-POWERED SOFTWARE RECOVERY
          </span>

          <span>
            v1.0 PROTOTYPE
          </span>

        </footer>

      </main>

    </div>
  );
}


/* PIPELINE STEP */

function PipelineStep({
  number,
  title,
  description,
  state,
}) {

  return (
    <div
      className={`pipeline-step ${state}`}
    >

      <div className="step-top">

        <div className="step-number">
          {number}
        </div>

        <div className="step-indicator">

          {state === "done" &&
            "✓"}

          {state === "running" && (
            <span className="mini-spinner" />
          )}

        </div>

      </div>


      <div className="step-description">
        {description}
      </div>


      <div className="step-title">
        {title}
      </div>


      <div className="step-status">

        {state === "done"
          ? "COMPLETED"
          : state === "running"
            ? "RUNNING"
            : "STANDBY"}

      </div>

    </div>
  );
}


/* PIPELINE ARROW */

function PipelineArrow() {

  return (
    <div className="pipeline-arrow">
      →
    </div>
  );
}


export default App;