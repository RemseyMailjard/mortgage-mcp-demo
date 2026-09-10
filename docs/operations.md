# Operations and releases

## Supported runtime

The packaged entry point and container support local stdio only. A hosted transport is not a
supported deployment until the security gates in `security-and-privacy.md` are complete.

Build and test the Python release artifact:

```powershell
uv sync --frozen --all-extras --dev
uv run pytest
uv build
```

Build and run the non-root container over stdin/stdout:

```powershell
docker build --tag mortgage-mcp-demo:local .
docker run --interactive --rm mortgage-mcp-demo:local
```

## Observability

- The `health` MCP tool verifies protocol initialization and process responsiveness.
- Successful calculation/comparison operations emit an event name and random correlation ID.
- Customer financial inputs are intentionally absent from logs, traces, and metrics.
- Process exit, MCP error results, and rate-provider failures are operational failure signals.
- Hosted metrics and tracing remain disabled until their data handling is reviewed.

## Rate refresh and failure behavior

Demo rates are versioned JSON with effective and expiry dates. Review the source, replace the
fixture, run all tests, and release it through a pull request. Missing, unmatched, or stale rates
fail closed with `RateDataUnavailableError`; never extend an expiry date without source approval.

## Release procedure

1. Confirm CI, dependency review, and security review pass on `main`.
2. Update the package version and changelog for the intended release.
3. Build from a clean checkout with `uv sync --frozen --no-dev` and `uv build`.
4. Tag the exact reviewed commit using semantic versioning, for example `v0.1.0`.
5. Publish artifacts from that tag and record their checksums and deployment configuration.
6. Run an MCP initialization, health call, and representative calculation after deployment.

## Rollback

Redeploy the preceding immutable image or package version, then run the same smoke calls. If the
incident involves incorrect rate data, disable calculations until an approved catalog is restored;
do not silently serve stale data. Preserve correlation IDs and release metadata for investigation,
without adding customer inputs to incident records.