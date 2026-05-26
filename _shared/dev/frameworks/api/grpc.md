# gRPC Framework

Loaded by Apply when .proto files or grpc in dependencies are detected.

## Version baseline

gRPC 1.60+. Declare: language (Go, Python, Rust, Node, Java); buf or protoc for code generation.

## Service definition

```protobuf
// user.proto
syntax = "proto3";

package user.v1;
option go_package = "github.com/example/api/user/v1";

import "google/protobuf/timestamp.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (stream User);    // server streaming
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}

message GetUserRequest {
  string user_id = 1;
}

message GetUserResponse {
  User user = 1;
}

message User {
  string user_id = 1;
  string email = 2;
  google.protobuf.Timestamp created_at = 3;
}
```

## Service types

| Type | Definition | Use |
|---|---|---|
| Unary | `rpc Method(Req) returns (Resp)` | Standard request/response |
| Server streaming | `rpc Method(Req) returns (stream Resp)` | Server pushes multiple responses |
| Client streaming | `rpc Method(stream Req) returns (Resp)` | Client sends multiple requests |
| Bidirectional | `rpc Method(stream Req) returns (stream Resp)` | Full duplex chat/sync |

Spec must declare which service type each RPC uses and why.

## Status codes

gRPC status codes replace HTTP status codes:

| gRPC status | Equivalent to | When |
|---|---|---|
| OK | 200 | Success |
| INVALID_ARGUMENT | 400 | Bad request / validation error |
| UNAUTHENTICATED | 401 | No credentials |
| PERMISSION_DENIED | 403 | Has credentials, no permission |
| NOT_FOUND | 404 | Resource not found |
| ALREADY_EXISTS | 409 | Duplicate |
| RESOURCE_EXHAUSTED | 429 | Rate limited |
| INTERNAL | 500 | Server error |
| UNAVAILABLE | 503 | Service down |

Always return a status code + status message. Never return OK with an error payload.

## Versioning

Protobuf backward compatibility rules:
- Never remove a field — mark it `reserved` instead
- Never change a field number — it determines wire encoding
- Never change a field type to an incompatible type
- Adding new fields is backward compatible (old clients ignore them)

Package versioning: `package user.v1` → `package user.v2` for breaking changes. Both versions can coexist.

## Authentication

gRPC over TLS. Authentication options:
- **Per-call metadata**: `Authorization: Bearer <token>` in metadata (equivalent to HTTP header)
- **mTLS**: mutual TLS; both client and server present certificates
- **Channel credentials + call credentials**: combine TLS transport with per-call auth

```go
// Client with metadata auth
ctx := metadata.AppendToOutgoingContext(ctx, "authorization", "Bearer "+token)
resp, err := client.GetUser(ctx, req)
```

## Interceptors

```go
// Server-side interceptor (middleware equivalent)
func authInterceptor(ctx context.Context, req any, info *grpc.UnaryServerInfo, 
                     handler grpc.UnaryHandler) (any, error) {
    token := metadata.ValueFromIncomingContext(ctx, "authorization")
    if !validateToken(token) {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }
    return handler(ctx, req)
}

server := grpc.NewServer(grpc.UnaryInterceptor(authInterceptor))
```

Spec must declare: which interceptors run on which services.

## Reflection and discovery

Enable server reflection in development — allows tools like `grpcurl` to discover services:
```go
reflection.Register(server)
```

Disable or restrict in production to avoid exposing service structure.
