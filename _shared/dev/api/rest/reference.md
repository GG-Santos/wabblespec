# REST API Consumption Reference

> **Type:** API reference | Loaded by platform packages on demand.

---

## Non-Negotiable Rules

1. **Single configured client per service.** One HTTP client instance with base URL, auth, and retry policy — not ad-hoc `fetch()` calls scattered through code.
2. **Retry policy declared.** Which status codes retry, how many times, with what backoff.
3. **Exponential backoff with jitter.** Never fixed-interval retry — causes thundering herd.
4. **Timeout on every request.** No request without a connect timeout and read timeout.

---

## Client Configuration

```typescript
// Single configured client — not raw fetch() per call
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.API_BASE_URL,
  timeout: 10_000,           // 10s total — set based on SLO
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
});

// Auth interceptor — token injected centrally
apiClient.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${getToken()}`;
  return config;
});

// Response error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log, transform, or re-throw with context
    throw new ApiError(error.response?.status, error.message);
  }
);
```

```python
# Python: requests Session — single configured session
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {get_token()}",
    "Accept": "application/json",
})
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))
```

---

## Retry Policy

```
Retryable status codes:
  429 Too Many Requests — respect Retry-After header if present
  500 Internal Server Error — transient server error
  502 Bad Gateway — upstream timeout
  503 Service Unavailable — server overloaded
  504 Gateway Timeout — upstream timeout

Non-retryable:
  400 Bad Request — fix the request
  401 Unauthorized — refresh token, then retry once
  403 Forbidden — do not retry
  404 Not Found — do not retry
  422 Unprocessable Entity — do not retry

Max retries: 3 (configurable per endpoint criticality)
```

---

## Exponential Backoff with Jitter

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  baseDelayMs = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxAttempts || !isRetryable(err)) throw err;
      const delay = baseDelayMs * 2 ** (attempt - 1);
      const jitter = Math.random() * delay * 0.3;  // ±30% jitter
      await sleep(delay + jitter);
    }
  }
  throw new Error('unreachable');
}
```

**Jitter prevents thundering herd:** Without jitter, all retrying clients hit the server simultaneously after each backoff interval.

---

## Timeout Strategy

```
Connect timeout: 3–5s   — how long to wait for TCP connection
Read timeout:   10–30s  — how long to wait for response after connected
Total timeout:  varies  — sum of connect + read + retry budget

Set both separately where possible. A 10s "timeout" that only covers read
will hang for minutes if DNS or TCP is slow.
```

```typescript
// axios: separate timeouts
const client = axios.create({
  timeout: 10_000,                    // total timeout
  httpAgent: new http.Agent({ timeout: 3_000 }),   // socket connect timeout
});
```

---

## Idempotency Keys

For non-idempotent POST/DELETE operations, send an idempotency key:

```typescript
await apiClient.post('/payments', payload, {
  headers: {
    'Idempotency-Key': crypto.randomUUID(),  // unique per logical operation
  },
});
// Safe to retry — server deduplicates on key
```

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Thundering herd on upstream failure | Fixed-interval retry | Exponential backoff + jitter |
| Request hangs indefinitely | No timeout | Set connect + read timeout on every client |
| Auth token expired mid-session | No refresh logic | 401 interceptor: refresh token, retry once |
| Retrying non-retryable errors | Retry on 400/422 | Allowlist retryable status codes explicitly |
| Multiple client instances | Ad-hoc fetch() calls | Single configured client per service |
