# API/Service Verification Gates

Registered with Verifier at platform activation. All gates blocking before Delivery wave.

---

## Gate 1: Auth Enforcement

**Check:** Every protected endpoint returns 401 for unauthenticated requests, with no side effects.

**Method:**
```bash
# For each protected endpoint in the inventory:
curl -s -o /dev/null -w "%{http_code}" http://<host>/<endpoint>
# Expected: 401

# Verify no side effects (e.g., check DB write count before and after)
```

**Pass:** Every protected endpoint returns 401 without an Authorization header. No DB writes or state changes occur.
**Fail:** Any protected endpoint returns 2xx, 3xx, or 4xx (other than 401/405) without auth.

---

## Gate 2: Health Endpoint

**Check:** /health returns 200 regardless of dependency state. No DB access.

**Method:**
```bash
# With DB connection blocked:
curl -s -w "\nHTTP %{http_code}" http://<host>/health
# Expected: HTTP 200, response time < 50ms

time curl -s http://<host>/health
# Expected: real < 0.050s
```

**Pass:** 200 within 50ms even when database is unreachable.
**Fail:** Non-200 response, or response time > 50ms, or response varies with DB state.

---

## Gate 3: Readiness Endpoint

**Check:** /ready returns 503 when a declared dependency is unreachable.

**Method:**
```bash
# Normal conditions:
curl -s -w "\nHTTP %{http_code}" http://<host>/ready
# Expected: HTTP 200

# With DB unreachable (block port or set invalid DATABASE_URL):
curl -s -w "\nHTTP %{http_code}" http://<host>/ready
# Expected: HTTP 503, body names unavailable dependency
```

**Pass:** 200 under normal conditions. 503 with dependency name in body when dependency is down.
**Fail:** Returns 200 when dependency is down, or returns 503 under normal conditions.

---

## Gate 4: No Secrets in Logs

**Check:** Auth tokens and API keys do not appear in log output.

**Method:**
```bash
KNOWN_TOKEN="wbs-gate4-test-$(date +%s)"

# Send request with known token value
curl -s -H "Authorization: Bearer $KNOWN_TOKEN" http://<host>/api/<any-endpoint>

# Wait for log flush, then search logs
docker logs <container> 2>&1 | grep -F "$KNOWN_TOKEN"
# OR for file-based logs:
grep -r "$KNOWN_TOKEN" /var/log/<service>/
```

**Pass:** Zero matches for the token value in any log output.
**Fail:** Token value appears in any log line.

---

## Gate 5: No Internals in Error Responses

**Check:** 500 error responses contain no stack traces, internal paths, or database details.

**Method:**
```bash
# Trigger a 500 (use a known trigger from the test suite, or send malformed internal state)
RESPONSE=$(curl -s -X POST http://<host>/api/<endpoint> \
  -H "Authorization: Bearer $VALID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '<500-triggering-payload>')

echo "$RESPONSE" | python3 -c "
import sys, json, re
body = sys.stdin.read()
forbidden_patterns = [
    r'at \w+ \(',        # JS stack frame
    r'File \".*\.py\"',  # Python stack frame
    r'goroutine \d+',    # Go panic
    r'SELECT.*FROM',     # SQL query
    r'/home/|/var/|/app/', # internal path
]
for pattern in forbidden_patterns:
    if re.search(pattern, body):
        print(f'FAIL: pattern found: {pattern}')
        sys.exit(1)
print('PASS: no internals found')
"
```

**Pass:** Response body matches declared error schema. No stack traces, paths, or query text.
**Fail:** Any forbidden pattern found in response body.

---

## Gate 6: Structured Log Format

**Check:** Every request log line is valid JSON containing required fields.

**Method:**
```bash
# Send 5 requests, capture logs, validate each line
for i in 1 2 3 4 5; do
  curl -s -H "Authorization: Bearer $VALID_TOKEN" http://<host>/api/<endpoint> > /dev/null
done

docker logs <container> 2>&1 | python3 - <<'EOF'
import sys, json

required_fields = ['timestamp', 'level', 'method', 'path', 'status_code', 'duration_ms']
failures = []

for i, line in enumerate(sys.stdin, 1):
    line = line.strip()
    if not line:
        continue
    try:
        entry = json.loads(line)
        missing = [f for f in required_fields if f not in entry]
        if missing:
            failures.append(f'Line {i}: missing fields {missing}')
    except json.JSONDecodeError:
        failures.append(f'Line {i}: not valid JSON: {line[:80]}')

if failures:
    for f in failures:
        print(f'FAIL: {f}')
    sys.exit(1)
else:
    print('PASS: all log lines valid JSON with required fields')
EOF
```

**Pass:** Zero parse failures. All required fields present on request log lines.
**Fail:** Any log line is not valid JSON, or any required field is absent.

---

## Gate 7: Parameterized Queries (Code Review)

**Check:** No user-supplied value concatenated into a query string.

**Method (static analysis):**
```bash
# Python — string interpolation in query context
grep -rn \
  -e 'execute(f"' \
  -e 'execute(".*+' \
  -e "execute('.*+" \
  src/ --include="*.py"

# TypeScript/JavaScript
grep -rn \
  -e 'query(`' \
  -e 'query(".*\${' \
  src/ --include="*.ts" --include="*.js"

# Go
grep -rn \
  -e 'Sprintf.*SELECT\|Sprintf.*INSERT\|Sprintf.*UPDATE\|Sprintf.*DELETE' \
  ./ --include="*.go"
```

**Pass:** Zero matches. All queries use parameterized placeholders.
**Fail:** Any match. Each match is a potential SQL injection vulnerability — must be fixed before Delivery.

---

## Gate 8: Rate Limit Enforcement

**Check:** 429 returned at declared limit. Retry-After header present.

**Method:**
```bash
# Set LIMIT to the declared per-client limit for the endpoint under test
LIMIT=100
ENDPOINT="http://<host>/api/<rate-limited-endpoint>"
FOUND_429=false

for i in $(seq 1 $((LIMIT + 10))); do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}\t%{header_json}" \
    -H "Authorization: Bearer $VALID_TOKEN" "$ENDPOINT")
  STATUS=$(echo "$RESPONSE" | cut -f1)
  if [ "$STATUS" = "429" ]; then
    FOUND_429=true
    # Verify Retry-After header present
    HEADERS=$(echo "$RESPONSE" | cut -f2)
    echo "$HEADERS" | python3 -c "
import sys, json
h = json.load(sys.stdin)
if 'retry-after' not in {k.lower(): v for k,v in h.items()}:
    print('FAIL: 429 returned but no Retry-After header')
    sys.exit(1)
else:
    print('PASS: 429 with Retry-After')
"
    break
  fi
done

$FOUND_429 || echo "FAIL: 429 never returned after $((LIMIT + 10)) requests"
```

**Pass:** 429 returned after declared limit is reached. Retry-After header present on 429 response.
**Fail:** No 429 returned, or 429 returned without Retry-After header.

---

## Gate 9: Container Lifecycle

**Check:** Image builds, starts cleanly, passes /health, and exits 0 on SIGTERM.

**Method:**
```bash
IMAGE="<service>:gate9-$(date +%s)"

# Build
docker build -t "$IMAGE" . || { echo "FAIL: build failed"; exit 1; }

# Start
CONTAINER=$(docker run -d \
  -p 18080:8080 \
  -e DATABASE_URL="$TEST_DB_URL" \
  -e LOG_LEVEL=info \
  "$IMAGE")

# Wait for health (max 15s)
READY=false
for i in $(seq 1 15); do
  sleep 1
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:18080/health 2>/dev/null)
  if [ "$STATUS" = "200" ]; then READY=true; break; fi
done

$READY || { echo "FAIL: /health did not return 200 within 15s"; docker rm -f "$CONTAINER"; exit 1; }

# Graceful shutdown
docker stop "$CONTAINER"   # sends SIGTERM, waits 10s
EXIT_CODE=$(docker inspect "$CONTAINER" --format='{{.State.ExitCode}}')

docker rm "$CONTAINER"
docker rmi "$IMAGE"

if [ "$EXIT_CODE" = "0" ]; then
  echo "PASS: container exited 0 on SIGTERM"
else
  echo "FAIL: container exited $EXIT_CODE (expected 0)"
  exit 1
fi
```

**Pass:** Build succeeds. /health returns 200 within 15s. SIGTERM causes exit code 0.
**Fail:** Build fails, /health does not return 200 within 15s, or exit code is non-zero.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Auth enforcement: 401 on all protected endpoints without credentials | Yes |
| 2 | Health endpoint: 200 within 50ms, no DB dependency | Yes |
| 3 | Readiness endpoint: 503 when dependency is down | Yes |
| 4 | No secrets in logs: token value absent from all log output | Yes |
| 5 | No internals in error responses: no stack traces, paths, or query text | Yes |
| 6 | Structured log format: every request line is valid JSON with required fields | Yes |
| 7 | Parameterized queries only: no user-input concatenation in query strings | Yes |
| 8 | Rate limit enforcement: 429 at declared limit with Retry-After header | Yes |
| 9 | Container lifecycle: builds, starts healthy, exits 0 on SIGTERM | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
