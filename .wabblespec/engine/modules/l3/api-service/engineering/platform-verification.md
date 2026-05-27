# API/Service Engineering — Platform Verification

How to run and interpret the API/Service verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# From project root, with service running locally:
python scripts/run-platform-gates.py --platform api-service --base-url http://localhost:8080

# Or manually per gate — see gate descriptions in verification/gates.md
```

**Prerequisites before running gates:**
1. Service is running (local or test environment)
2. Test database seeded with fixture data
3. At least one valid auth token available (for authenticated endpoint tests)
4. At least one invalid/expired token available (for 401 tests)

---

## Per-Gate Verification Commands

### Gate 1: Auth enforcement
```bash
# Every protected endpoint must return 401 with no auth header
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/<endpoint>
# Expected: 401

# Verify no side effect (e.g., no DB write occurred)
# Check DB state is unchanged after unauthenticated request
```

### Gate 2: Health endpoint
```bash
# Kill or block DB connection, then:
curl -s http://localhost:8080/health
# Expected: 200, body: {"status":"ok"}

# Measure response time:
time curl -s http://localhost:8080/health
# Expected: real < 0.05s
```

### Gate 3: Readiness endpoint
```bash
# Normal conditions:
curl -s http://localhost:8080/ready
# Expected: 200

# With DB unreachable:
# (block DB port or set DATABASE_URL to invalid host)
curl -s http://localhost:8080/ready
# Expected: 503, body names unavailable dependency
```

### Gate 4: No secrets in logs
```bash
# Send a request with a known token value
AUTH_TOKEN="test-token-known-value-abc123"
curl -H "Authorization: Bearer $AUTH_TOKEN" http://localhost:8080/api/<endpoint>

# Grep service logs for the token value
docker logs <container> 2>&1 | grep "test-token-known-value-abc123"
# Expected: zero matches
```

### Gate 5: No internals in error responses
```bash
# Trigger a 500 — e.g., pass invalid data that causes unhandled exception
curl -s -X POST http://localhost:8080/api/<endpoint> \
  -H "Authorization: Bearer $VALID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '<payload that triggers 500>'

# Inspect response body for internal details
# Must not contain: stack trace, file path, database query, hostname
```

### Gate 6: Structured log format
```bash
docker logs <container> 2>&1 | while IFS= read -r line; do
  echo "$line" | python3 -c "import sys, json; json.load(sys.stdin)" 2>&1
done | grep -c "error"
# Expected: 0 (all log lines are valid JSON)

# Verify required fields present on a sample request log:
docker logs <container> 2>&1 | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        entry = json.loads(line.strip())
        required = ['timestamp','level','method','path','status_code','duration_ms']
        missing = [f for f in required if f not in entry]
        if missing:
            print(f'MISSING: {missing} in: {line.strip()[:100]}')
    except: pass
"
```

### Gate 7: SQL injection (parameterized queries)
```bash
# Code review — grep for string interpolation in query context:
grep -rn "f\"SELECT\|f'SELECT\|\"SELECT.*+\|'SELECT.*+" src/ --include="*.py"
grep -rn 'fmt.Sprintf.*SELECT\|fmt.Sprintf.*INSERT\|fmt.Sprintf.*UPDATE' ./ --include="*.go"
grep -rn 'query.*\+.*req\|query.*\${' src/ --include="*.ts"
# Expected: zero matches

# Dynamic test (if SQL injection test suite available):
# Send ' OR '1'='1 as a filter parameter and verify 400, not data leak
```

### Gate 8: Rate limit
```bash
# Send requests at limit+1 rate and capture first 429
for i in $(seq 1 110); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $VALID_TOKEN" \
    http://localhost:8080/api/<rate-limited-endpoint>)
  echo "Request $i: $STATUS"
done | grep "429" | head -5
# Expected: 429 appears after declared limit, with Retry-After header
```

### Gate 9: Container lifecycle
```bash
# Build
docker build -t <service>:test .

# Start
docker run -d --name test-service -p 8080:8080 \
  -e DATABASE_URL="$TEST_DB_URL" \
  -e LOG_LEVEL=info \
  <service>:test

# Wait for ready
until curl -sf http://localhost:8080/health; do sleep 1; done

# Verify health
curl -s http://localhost:8080/health  # Expected: 200

# Graceful shutdown
docker stop test-service  # sends SIGTERM, waits 10s, then SIGKILL
docker inspect test-service --format='{{.State.ExitCode}}'  # Expected: 0

# Cleanup
docker rm test-service
```

---

## Interpreting Results

**Gate FAIL — auth not enforced:**
- Find all route registrations and verify auth middleware is applied globally or per-route
- Check middleware order: auth must be before handler, not after

**Gate FAIL — secrets in logs:**
- Find all log statements that include request headers or body
- Add a scrubbing step: replace Authorization header value with `[REDACTED]` before logging

**Gate FAIL — internals in error response:**
- Find the global error handler and verify it formats errors via RFC 7807 serializer, not raw exception toString
- Ensure framework's default error handler is replaced by the custom one

**Gate FAIL — log lines not valid JSON:**
- Find any `console.log` / `print()` / `fmt.Println` calls not going through the structured logger
- Replace all with structured logger calls

**Gate FAIL — container exit non-zero:**
- Check SIGTERM handler is registered before server binds
- Ensure drain timeout does not exceed terminationGracePeriodSeconds
- Check for connections that hold open beyond drain window

---

## Regression Prevention

After gates pass:
1. Record gate results in platform activation receipt
2. Add critical gates to CI (auth, secrets-in-logs, container lifecycle)
3. Any change to middleware stack, error handling, or logging requires re-running gates 1–6
4. Gate results are not cached — run fresh on each release candidate
