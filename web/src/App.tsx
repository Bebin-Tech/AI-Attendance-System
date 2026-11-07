import { useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("Checking service readiness…");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const timeout = window.setTimeout(() => controller.abort(), 5000);
    fetch("/api/v1/health/ready", { signal: controller.signal })
      .then(async (response) => {
        const body: unknown = await response.json();
        if (!active) return;
        const ready =
          response.ok &&
          typeof body === "object" &&
          body !== null &&
          "status" in body &&
          body.status === "ready";
        setStatus(
          ready
            ? "API, database and cache are ready."
            : "Service is not ready. Check the database and cache.",
        );
      })
      .catch(() => {
        if (active)
          setStatus("Cannot reach the API. Check your connection and retry.");
      })
      .finally(() => window.clearTimeout(timeout));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timeout);
    };
  }, [retry]);

  return (
    <main>
      <header>
        <span className="brand">AIFAMS</span>
        <span>System foundation · Phase 1</span>
      </header>
      <section aria-labelledby="title">
        <p className="eyebrow">AI Face Attendance Management System</p>
        <h1 id="title">Trust begins with a reliable foundation.</h1>
        <p>
          The platform is being built in verified phases. Attendance and
          biometric workflows will become available after their security and
          consent checks are implemented.
        </p>
        <div className="status">
          <h2>Service readiness</h2>
          <p role="status">{status}</p>
          <button onClick={() => setRetry((value) => value + 1)}>
            Check again
          </button>
        </div>
        <a href="/api/v1/docs">
          Open API documentation <span aria-hidden="true">↗</span>
        </a>
      </section>
      <footer>Consent first. Audited actions. Tenant isolation.</footer>
    </main>
  );
}
