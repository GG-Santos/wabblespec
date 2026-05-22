# gRPC API Consumption Reference

> **Type:** API reference | Loaded by platform packages on demand.

---

## Non-Negotiable Rules

1. **Deadline on every RPC.** No RPC without a deadline. Unbounded RPCs block indefinitely on failure.
2. **`DEADLINE_EXCEEDED` is never retried.** Deadline means the work is no longer needed. Retry wastes resources and may cause duplicate effects.
3. **Stubs generated from `.proto` files.** Never hand-write gRPC client code.
4. **TLS always in production.** No plaintext gRPC outside local development.

---

## Proto and Code Generation

```protobuf
// user.proto
syntax = "proto3";
package user.v1;

service UserService {
  rpc GetUser (GetUserRequest) returns (GetUserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream User);
}

message GetUserRequest { string id = 1; }
message GetUserResponse { User user = 1; }
message User {
  string id = 1;
  string email = 2;
  google.protobuf.Timestamp created_at = 3;
}
```

```bash
# Generate stubs
# Node (grpc-tools):
grpc_tools_node_protoc --js_out=import_style=commonjs:. --grpc_out=grpc_js:. user.proto

# Python (grpcio-tools):
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto

# Go:
protoc --go_out=. --go-grpc_out=. user.proto

# Generated files — never edit. Add to .gitignore or commit as build artifacts per project convention.
```

---

## Deadline on Every RPC

```typescript
// Node — deadline as absolute time
const deadline = new Date();
deadline.setSeconds(deadline.getSeconds() + 5);  // 5s from now

const response = await userClient.getUser(
  { id: userId },
  { deadline }
);

// Without deadline — hangs indefinitely if server is down
const response = await userClient.getUser({ id: userId });  // NEVER in production
```

```python
# Python — deadline as relative seconds
try:
    response = stub.GetUser(
        user_pb2.GetUserRequest(id=user_id),
        timeout=5.0  # seconds
    )
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        # Do NOT retry — deadline means caller gave up
        raise TimeoutError(f"GetUser timed out for user {user_id}")
```

```go
// Go — context with timeout
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()  // always defer cancel to avoid context leak

resp, err := client.GetUser(ctx, &userpb.GetUserRequest{Id: userID})
if err != nil {
    st, _ := status.FromError(err)
    if st.Code() == codes.DeadlineExceeded {
        return fmt.Errorf("GetUser deadline exceeded: %w", err)
        // Do NOT retry
    }
}
```

---

## Retry Policy

```
Retryable status codes:
  UNAVAILABLE      — server temporarily unavailable, safe to retry
  RESOURCE_EXHAUSTED — rate limited, retry with backoff

Never retry:
  DEADLINE_EXCEEDED — caller's window expired; retry wastes resources
  INVALID_ARGUMENT  — client bug; retry won't help
  NOT_FOUND         — resource doesn't exist; retry won't help
  PERMISSION_DENIED — access denied; retry won't help
  UNAUTHENTICATED   — refresh credentials, then retry once

Retry with exponential backoff + jitter. Max 3 attempts.
```

Service config retry policy (gRPC built-in):
```json
{
  "methodConfig": [{
    "name": [{"service": "user.v1.UserService"}],
    "retryPolicy": {
      "maxAttempts": 3,
      "initialBackoff": "0.5s",
      "maxBackoff": "10s",
      "backoffMultiplier": 2,
      "retryableStatusCodes": ["UNAVAILABLE"]
    }
  }]
}
```

---

## Streaming RPCs

```go
// Server-streaming: receive multiple responses
stream, err := client.ListUsers(ctx, &userpb.ListUsersRequest{})
if err != nil { return err }

for {
    user, err := stream.Recv()
    if err == io.EOF { break }  // stream complete
    if err != nil { return fmt.Errorf("ListUsers stream: %w", err) }
    process(user)
}

// Client-streaming: send multiple requests
stream, err := client.BatchCreate(ctx)
for _, item := range items {
    if err := stream.Send(&pb.CreateRequest{Item: item}); err != nil {
        return err
    }
}
resp, err := stream.CloseAndRecv()
```

**Deadline applies to the entire stream duration** — set longer deadline for long-running streams or use bidirectional streaming with per-message timeouts.

---

## TLS Configuration

```go
// Production: TLS required
creds, err := credentials.NewClientTLSFromFile("ca.crt", "")
conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(creds))

// Mutual TLS
creds, err := credentials.NewTLS(&tls.Config{
    Certificates: []tls.Certificate{clientCert},
    RootCAs: caCertPool,
})

// Development only: insecure (never production)
conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
```

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Indefinite hang | No deadline on RPC | Set deadline/timeout on every call |
| Retry loop on timeout | Retrying `DEADLINE_EXCEEDED` | Only retry `UNAVAILABLE`; never retry `DEADLINE_EXCEEDED` |
| Context leak | `cancel()` not deferred | Always `defer cancel()` after `WithTimeout` |
| Stream not drained | Error path skips `stream.Recv()` loop | Always drain or explicitly cancel context to close stream |
| Plaintext in production | `insecure.NewCredentials()` not removed | Gate insecure on build flag; default to TLS |
