# Realtime / WebSocket Reference

> **Type:** API reference | Loaded by platform packages on demand.
> **Applies to:** WebSocket, Socket.IO, SSE, MQTT over WS

---

## Non-Negotiable Rules

1. **Single WebSocket per logical session.** One connection per user session — not one per component or tab.
2. **Auth token in first message.** Authenticate immediately after `open` event — before sending any application messages.
3. **Heartbeat with dead-connection detection.** Ping/pong or application-level heartbeat — detect and close dead connections.
4. **Reconnect with exponential backoff.** Never fixed-interval reconnect — thundering herd on server restart.

---

## Single Connection per Session

```typescript
// WRONG: component creates its own WebSocket
function ChatComponent() {
  useEffect(() => {
    const ws = new WebSocket(url);  // multiplied per mount — connection storm
    return () => ws.close();
  }, []);
}

// CORRECT: single shared connection managed outside components
// ws-manager.ts
class WebSocketManager {
  private socket: WebSocket | null = null;
  private listeners = new Map<string, Set<(data: unknown) => void>>();

  connect(url: string, token: string) {
    if (this.socket?.readyState === WebSocket.OPEN) return;  // already connected
    this.socket = new WebSocket(url);

    this.socket.addEventListener('open', () => {
      // Step 1: authenticate immediately
      this.send({ type: 'AUTH', token });
    });

    this.socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data as string);
      this.listeners.get(message.type)?.forEach(fn => fn(message));
    });

    this.socket.addEventListener('close', (event) => {
      if (!event.wasClean) this.scheduleReconnect(url, token);
    });
  }

  on(type: string, fn: (data: unknown) => void) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type)!.add(fn);
    return () => this.listeners.get(type)?.delete(fn);  // returns cleanup fn
  }
}

export const wsManager = new WebSocketManager();  // singleton
```

---

## Authentication Flow

```
1. Client opens WebSocket connection
2. Server accepts TCP/WS handshake (no auth yet)
3. Client sends AUTH message immediately in 'open' handler:
   { type: "AUTH", token: "<bearer-token>" }
4. Server validates token:
   - Valid: sends AUTH_OK, marks connection authenticated
   - Invalid: sends AUTH_FAIL, closes connection
5. Client discards all messages received before AUTH_OK

Timeout: if AUTH not sent within 5s of open, server closes connection
```

**Never put auth in the URL query string** (`ws://host?token=xxx`). URL appears in server logs — token is exposed.

---

## Heartbeat / Dead Connection Detection

```typescript
class WebSocketManager {
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private pongTimeout: ReturnType<typeof setTimeout> | null = null;

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket?.readyState !== WebSocket.OPEN) return;
      this.send({ type: 'PING' });

      // If no PONG within 5s, connection is dead
      this.pongTimeout = setTimeout(() => {
        this.socket?.close();  // triggers reconnect via 'close' handler
      }, 5000);
    }, 30_000);  // ping every 30s
  }

  handlePong() {
    clearTimeout(this.pongTimeout!);  // PONG received — connection alive
  }

  stopHeartbeat() {
    clearInterval(this.heartbeatInterval!);
    clearTimeout(this.pongTimeout!);
  }
}
```

**Why application-level heartbeat:** TCP keepalive is not reliable across proxies, load balancers, and NAT. Application-level ping/pong detects dead connections that TCP considers open.

---

## Reconnect with Exponential Backoff

```typescript
private reconnectAttempt = 0;

private scheduleReconnect(url: string, token: string) {
  const baseDelay = 1000;
  const maxDelay = 60_000;
  const delay = Math.min(baseDelay * 2 ** this.reconnectAttempt, maxDelay);
  const jitter = Math.random() * delay * 0.3;

  setTimeout(() => {
    this.reconnectAttempt++;
    this.connect(url, token);
  }, delay + jitter);
}

// Reset counter on successful connection
private onAuthOk() {
  this.reconnectAttempt = 0;
}
```

**Backoff schedule:** 1s → 2s → 4s → 8s → 16s → 32s → 60s (capped). Jitter prevents synchronized reconnect storm on server restart.

---

## Message Queue for Offline/Reconnecting

```typescript
private messageQueue: unknown[] = [];

send(message: unknown) {
  if (this.socket?.readyState === WebSocket.OPEN && this.authenticated) {
    this.socket.send(JSON.stringify(message));
  } else {
    this.messageQueue.push(message);  // queue while disconnected
  }
}

private flushQueue() {
  while (this.messageQueue.length > 0) {
    const msg = this.messageQueue.shift();
    this.socket!.send(JSON.stringify(msg));
  }
}

// Call flushQueue after AUTH_OK
```

**Queue size bounded.** Drop oldest if queue exceeds limit — don't buffer indefinitely.

---

## Server-Sent Events (SSE) — Alternative for Server→Client Only

```typescript
// SSE: simpler than WebSocket for unidirectional server→client streams
const evtSource = new EventSource('/api/events', {
  withCredentials: true  // send cookies for auth
});

evtSource.addEventListener('update', (event) => {
  const data = JSON.parse(event.data);
  handle(data);
});

evtSource.onerror = () => {
  // Browser auto-reconnects SSE — no manual backoff needed
  // But check readyState to avoid acting on transient errors
};
```

**Use SSE when:** server pushes only, no client messages needed. Simpler than WebSocket, auto-reconnects, works through HTTP/2 multiplexing.

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Connection storm | One WS per component | Single managed singleton connection |
| Token in server logs | Auth in query string | Send token in first application message |
| Zombie connection | No heartbeat | Application-level ping/pong every 30s |
| Thundering herd on reconnect | Fixed-interval retry | Exponential backoff + jitter |
| Unauthenticated messages processed | No AUTH_OK gate | Buffer and discard messages until AUTH_OK received |
| Memory leak | Listener not removed on unmount | `on()` returns cleanup function — call it in component teardown |
