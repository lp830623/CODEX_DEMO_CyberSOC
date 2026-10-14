# Codex working agreement

This is a Codex Ambassador demonstration with synthetic data only.

- Read README.md and docs/architecture.md before changes.
- Preserve Next.js + TypeScript frontend and FastAPI backend. Keep API paths stable.
- No external AI API calls, GCP, BigQuery, production credentials, real recordings, telemetry, or external fonts.
- Use datasets/synthetic fixtures. Never fetch personal or company data.
- Keep deterministic analysis visibly labelled as DEMO, never claim it is a live model.
- Run backend tests, frontend tests, typecheck and build for relevant code changes.
- Run the Playwright user journey for UI behavior changes when a browser is available.
- A browser-only preview and the backend must implement the same domain semantics.
- Add meaningful regression tests for time windows, evidence and cross-record isolation.
- Work in small diffs; describe behavior, test results and remaining limits.
- No deployment or networking changes outside this demo.
