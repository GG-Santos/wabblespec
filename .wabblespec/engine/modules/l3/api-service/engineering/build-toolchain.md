# API/Service Engineering — Build Toolchain

## Node/TypeScript API

**Preferred framework:** Fastify (performance) or Express (ecosystem). NestJS for large structured services.

**Build:**
```bash
tsc --noEmit          # type check only — no emit
esbuild src/index.ts --bundle --platform=node --outfile=dist/server.js
# OR: tsup for dual output
```

**package.json requirements:**
```json
{
  "main": "dist/server.js",
  "engines": { "node": ">=20" },
  "scripts": {
    "build": "esbuild src/index.ts --bundle --platform=node --outfile=dist/server.js",
    "start": "node dist/server.js",
    "typecheck": "tsc --noEmit"
  }
}
```

**No postinstall scripts.** No arbitrary code at install time.

---

## Python API

**Preferred framework:** FastAPI (async, OpenAPI auto-generated). Flask or Django REST Framework for legacy compatibility.

**Packaging:** `pyproject.toml` (PEP 621). No `setup.py`.

**ASGI server:** Uvicorn (development) / Gunicorn + Uvicorn workers (production).

**Dependency pinning:**
```
requirements.txt — pinned exact versions for production
requirements-dev.txt — dev/test deps
```

**Build for container:**
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

---

## Go API

**Build:**
```bash
go build -ldflags "-X main.version=$(VERSION)" -o ./bin/server ./cmd/server
```

**Single binary.** No runtime dependencies. Minimal container image:
```dockerfile
FROM gcr.io/distroless/static
COPY bin/server /server
CMD ["/server"]
```

**go.sum:** Committed. Required for reproducible builds.

**CGO:** Disabled by default (`CGO_ENABLED=0`). Required for distroless/scratch images.

---

## Rust API

**Build:**
```bash
cargo build --release
```

**Container:** Copy release binary to distroless or scratch image.

**Cargo.lock:** Committed (this is a binary service, not a library).

---

## Container Build

**Dockerfile requirements (all languages):**

```dockerfile
# Multi-stage: build stage + minimal runtime stage
FROM <builder-image> AS build
# ... build steps ...

FROM <minimal-runtime-image>
# Non-root user required
RUN useradd -r -u 1001 appuser
USER appuser
# Expose only the service port
EXPOSE 8080
# Use exec form (no shell wrapper)
CMD ["/app/server"]
```

**Non-root user:** Required. Process must not run as root inside container.

**EXPOSE:** Declare the single service port. Match PORT env var default.

**No secrets in image:** No credentials, API keys, or connection strings baked into the image. All from env vars at runtime.

**Image tagging:**
- `<registry>/<service>:<git-sha>` — immutable tag for every build
- `<registry>/<service>:latest` — updated on main branch only, never in CI without a sha tag alongside

---

## Database Migrations

**Migration tool:** (declare per project — Flyway, Alembic, golang-migrate, Atlas, Prisma Migrate)

**Migration run strategy:**
[ ] Separate init container runs migrations before service starts (Kubernetes)
[ ] Service runs migrations on startup (acceptable for small services — document timeout risk)
[ ] Manual migration step in deploy pipeline

**Rollback:** Every migration must have a corresponding down migration. Test rollback before shipping.

**Zero-downtime migrations:** For tables with concurrent traffic:
1. Additive changes (new nullable column, new table) — safe to apply live
2. Rename/drop — requires multi-phase deploy (add new, backfill, remove reference, drop old)

---

## CI Pipeline Gates

Required before any release artifact is produced:

1. Type check / lint: `tsc --noEmit` / `ruff` / `go vet` / `cargo clippy` — zero errors
2. Unit tests pass
3. Integration tests pass (with test database / in-memory dependencies)
4. Container builds successfully: `docker build --no-cache`
5. Container starts and /health returns 200: `docker run -d ... && curl /health`
6. Container shuts down cleanly on SIGTERM (drain test)
7. Dependency audit: `npm audit` / `pip-audit` / `cargo audit` — zero critical/high
8. No secrets in image: `docker history --no-trunc` inspection, or dedicated scanner (Trivy)

---

## OpenAPI Spec Management

**Generation:**
[ ] Code-first: framework generates spec from code annotations (FastAPI, NestJS, tsoa)
[ ] Design-first: spec authored manually, code validated against it

**Contract testing:** Generated spec committed to repo. CI fails if generated spec differs from committed spec (prevents undocumented API drift).

**Spec location:** `openapi.yaml` at repo root or `api/openapi.yaml`.
