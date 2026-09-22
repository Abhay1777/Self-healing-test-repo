import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

export default function App() {

  const [repo, setRepo] = useState("");

  const [status, setStatus] = useState({
    running: false,
    success: null,
    attempts: 0,
    trace: [],
    diff: "",
    error: null,
    repository: null
  });

  const [message, setMessage] = useState("");


  async function refresh() {

    try {

      const response = await fetch(
        `${API}/status`,
        { cache: "no-store" }
      );

      const data = await response.json();

      setStatus(data);

    } catch {

      setMessage(
        "FastAPI backend is offline."
      );

    }
  }


  async function healRepository() {

    if (!repo.trim()) {

      setMessage(
        "Enter a GitHub repository URL first."
      );

      return;
    }

    setMessage(
      "Starting repository healing..."
    );

    try {

      const response = await fetch(
        `${API}/heal-repository`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            repo_url: repo
          })
        }
      );

      const data = await response.json();

      if (!data.accepted) {

        setMessage(
          data.message
        );

        return;
      }

      setMessage(
        "Repository healing started."
      );

      refresh();

    } catch {

      setMessage(
        "Could not connect to the backend."
      );

    }
  }


  async function healDemo() {

    setMessage(
      "Starting local demo..."
    );

    try {

      await fetch(
        `${API}/heal-demo`,
        {
          method: "POST"
        }
      );

      refresh();

    } catch {

      setMessage(
        "Could not start demo."
      );

    }
  }


  useEffect(() => {

    refresh();

    const timer = setInterval(
      refresh,
      700
    );

    return () => clearInterval(timer);

  }, []);


  const trace =
    status.trace || [];


  const agents = [
    ["AGENT 1", "TEST AGENT"],
    ["AGENT 2", "AI DEBUG"],
    ["PATCHER", "SAFE PATCHER"],
    ["AGENT 3", "VERIFICATION"]
  ];


  function completed(agent) {

    return trace.some(
      item =>
        item.agent === agent &&
        item.status === "success"
    );
  }


  function active(agent) {

    return trace.some(
      item =>
        item.agent === agent
    );
  }


  return (

    <div className="app">

      <header>

        <div className="brand">

          <div className="logo">
            SH
          </div>

          <div>
            <strong>
              SELF-HEAL GIT
            </strong>

            <small>
              Autonomous Software Healing
            </small>
          </div>

        </div>

        <div className="online">
          <span />
          SYSTEM ONLINE
        </div>

      </header>


      <main>


        <section className="hero">

          <div>

            <div className="eyebrow">
              AUTONOMOUS DEVELOPER INFRASTRUCTURE
            </div>

            <h1>
              Detect.
              <br />
              <em>Diagnose.</em>
              <br />
              Heal.
            </h1>

            <p>
              Give Self-Heal Git a GitHub repository.
              It clones the code, runs tests, diagnoses
              failures with AI, applies a validated patch,
              and verifies the result.
            </p>

          </div>


          <div className="status-card">

            <small>
              CURRENT STATUS
            </small>

            <h2>
              {status.running
                ? "HEALING"
                : status.success
                ? "HEALED"
                : status.success === false
                ? "FAILED"
                : "READY"}
            </h2>

            <div className="stat">
              <span>ATTEMPTS</span>
              <b>{status.attempts}</b>
            </div>

            <div className="stat">
              <span>EVENTS</span>
              <b>{trace.length}</b>
            </div>

          </div>

        </section>


        <section className="repository">

          <div className="eyebrow">
            GITHUB REPOSITORY
          </div>

          <h3>
            Heal a real repository
          </h3>

          <div className="repo-row">

            <input
              value={repo}
              onChange={
                e => setRepo(e.target.value)
              }
              placeholder="https://github.com/username/repository"
              disabled={status.running}
            />

            <button
              onClick={healRepository}
              disabled={status.running}
            >
              {status.running
                ? "HEALING..."
                : "ANALYZE & HEAL"}
            </button>

          </div>

          <button
            className="demo-button"
            onClick={healDemo}
            disabled={status.running}
          >
            RUN LOCAL DEMO
          </button>

          {message && (
            <div className="message">
              {message}
            </div>
          )}

        </section>


        <section>

          <div className="eyebrow">
            LIVE PIPELINE
          </div>

          <h3>
            Healing Workflow
          </h3>


          <div className="pipeline">

            {agents.map(
              (agent, index) => {

                const done =
                  completed(agent[0]);

                const started =
                  active(agent[0]);

                return (

                  <div
                    className={
                      "pipeline-card " +
                      (started ? "active " : "") +
                      (done ? "done" : "")
                    }
                    key={agent[0]}
                  >

                    <div className="number">
                      {done
                        ? "✓"
                        : index + 1}
                    </div>

                    <small>
                      {agent[0]}
                    </small>

                    <strong>
                      {agent[1]}
                    </strong>

                  </div>

                );

              }
            )}

          </div>

        </section>


        <section>

          <div className="eyebrow">
            EXECUTION TRACE
          </div>

          <h3>
            Agent Activity
          </h3>


          <div className="trace">

            {trace.length === 0 && (

              <div className="empty">
                No healing run yet.
              </div>

            )}


            {trace.map(
              (item, index) => (

                <div
                  className="trace-row"
                  key={index}
                >

                  <div
                    className={
                      "icon " +
                      item.status
                    }
                  >
                    {item.status === "success"
                      ? "✓"
                      : item.status === "error"
                      ? "!"
                      : "→"}
                  </div>

                  <div>

                    <strong>
                      {item.agent}
                    </strong>

                    <span
                      className={
                        "badge " +
                        item.status
                      }
                    >
                      {item.status}
                    </span>

                    <p>
                      {item.message}
                    </p>

                  </div>

                </div>

              )
            )}

          </div>

        </section>


        {status.diff && (

          <section>

            <div className="eyebrow">
              GIT DIFF
            </div>

            <h3>
              Generated Changes
            </h3>

            <pre className="diff">
              {status.diff}
            </pre>

          </section>

        )}


        {status.success && !status.running && (

          <div className="success">

            <b>
              ✓ HEALING VERIFIED
            </b>

            <span>
              Repository tests passed after the AI patch.
            </span>

          </div>

        )}


        {status.error && (

          <div className="error">

            <b>
              HEALING ERROR
            </b>

            <p>
              {status.error}
            </p>

          </div>

        )}

      </main>


      <footer>
        SELF-HEAL GIT
        <span>
          AUTONOMOUS AI SOFTWARE ENGINEERING
        </span>
      </footer>

    </div>

  );
}
