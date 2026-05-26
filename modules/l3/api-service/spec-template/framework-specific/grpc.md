# Framework-Specific Architecture: gRPC

> **Applies when:** `.proto` files detected in repo, or `grpc` / `@grpc/grpc-js` / `grpcio` in dependencies.
> Covers gRPC with proto3. Runtime: Go, Python, Node.js, or Java — declare in technical-spec.md.
> **Version authority:** proto3 syntax. gRPC 1.6x. Protobuf 4.x (Python) / protoc 25+.

---

## Service Definition First [REQUIRED]

The `.proto` file is the contract. Implementation follows from the contract — not the other way around. All consumers and producers must agree on the proto before coding begins.

```protobuf
// proto/products/v1/products.proto
syntax = "proto3";

package products.v1;
option go_package = "github.com/example/api/products/v1;productsv1";

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// Versioned package path — breaking changes require a new version (v2)
// Never edit published proto fields — only add new ones (field numbers are permanent)

service ProductService {
  // Unary — single request, single response
  rpc GetProduct(GetProductRequest) returns (Product);
  rpc CreateProduct(CreateProductRequest) returns (Product);

  // Server streaming — single request, stream of responses
  rpc ListProducts(ListProductsRequest) returns (stream Product);

  // Client streaming — stream of requests, single response
  rpc BatchCreateProducts(stream CreateProductRequest) returns (BatchCreateResponse);

  // Bidirectional streaming — stream both ways
  rpc SyncProducts(stream SyncRequest) returns (stream SyncResponse);
}

message Product {
  string id = 1;          // field number 1 — permanent; never reuse a deleted field number
  string name = 2;
  int64 price_cents = 3;  // money as integer cents — no floating point for currency
  string category_id = 4;
  google.protobuf.Timestamp created_at = 5;
  // Adding a new field later: assign next available number (6, 7, ...)
  // Removing a field: use 'reserved' — never just delete
}

message GetProductRequest {
  string id = 1;
}

message CreateProductRequest {
  string name = 1;
  int64 price_cents = 2;
  string category_id = 3;
}

message ListProductsRequest {
  int32 page_size = 1;
  string page_token = 2;  // cursor-based pagination for streaming
  string category_id = 3; // optional filter — empty string = no filter
}

message BatchCreateResponse {
  repeated Product products = 1;
  int32 failed_count = 2;
}
```

---

## Field Number Rules

Field numbers are **permanent**. Once a message is in production, existing field numbers cannot change or be reused.

```protobuf
message Product {
  reserved 6, 7;                    // field numbers no longer in use
  reserved "deprecated_field";      // field name no longer in use
  // Future additions start at 8
}
```

**Breaking changes** (require v2 package):
- Removing or renumbering a field
- Changing a field's type
- Changing a service method signature

**Non-breaking changes** (safe to add to existing version):
- Adding a new field with a new field number
- Adding a new RPC method to a service
- Adding a new service

---

## Error Handling — gRPC Status Codes

```go
// Go — use status package for typed errors
import (
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

func (s *productServer) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
    if req.Id == "" {
        return nil, status.Error(codes.InvalidArgument, "id is required")
    }
    product, err := s.repo.Get(ctx, req.Id)
    if errors.Is(err, ErrNotFound) {
        return nil, status.Errorf(codes.NotFound, "product %s not found", req.Id)
    }
    if err != nil {
        return nil, status.Error(codes.Internal, "failed to fetch product")
        // Never expose internal error details to clients
    }
    return toProto(product), nil
}
```

**gRPC status code mapping:**

| gRPC Code | HTTP equivalent | Use when |
|---|---|---|
| `OK` | 200 | Success |
| `InvalidArgument` | 400 | Client sent bad input |
| `NotFound` | 404 | Resource does not exist |
| `AlreadyExists` | 409 | Create failed — already exists |
| `PermissionDenied` | 403 | Authenticated but not authorized |
| `Unauthenticated` | 401 | Missing or invalid credentials |
| `ResourceExhausted` | 429 | Rate limit exceeded |
| `Unavailable` | 503 | Service temporarily down — safe to retry |
| `Internal` | 500 | Server error — do not expose details |
| `DeadlineExceeded` | 504 | Deadline passed before completion |

---

## Deadlines and Context Propagation

```go
// Always check ctx.Err() in long-running handlers
func (s *productServer) ListProducts(req *pb.ListProductsRequest, stream pb.ProductService_ListProductsServer) error {
    ctx := stream.Context()
    products, err := s.repo.List(ctx, req)
    if err != nil {
        return err
    }
    for _, p := range products {
        if ctx.Err() != nil {
            return status.Error(codes.Canceled, "client canceled")
        }
        if err := stream.Send(toProto(p)); err != nil {
            return err
        }
    }
    return nil
}
```

```go
// Client — always set a deadline
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()  // always defer cancel — prevents context leak

product, err := client.GetProduct(ctx, &pb.GetProductRequest{Id: "123"})
if status.Code(err) == codes.DeadlineExceeded {
    // handle timeout
}
```

**Rule:** Every client call must set a deadline. Servers must propagate context to downstream calls. Handlers that do not check `ctx.Err()` in loops will continue processing after the client cancels — wasted work and resource exhaustion.

---

## Interceptors (middleware equivalent)

```go
// Unary server interceptor
func loggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    log.Printf("method=%s duration=%s err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

// Auth interceptor — verify JWT from metadata
func authInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }
    tokens := md.Get("authorization")
    if len(tokens) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing token")
    }
    // validate token...
    return handler(ctx, req)
}

// Chain interceptors:
grpc.NewServer(
    grpc.ChainUnaryInterceptor(authInterceptor, loggingInterceptor, recoveryInterceptor),
)
```

---

## GWT Acceptance Scenarios

```
Given: a client sends a GetProduct request for a non-existent ID
When: the server handler runs
Then: the response status code is codes.NotFound (not codes.Internal)
      AND the error message does not contain a stack trace or internal path
      AND the client can distinguish NotFound from Internal errors via status code

Given: a client sets a 2-second deadline and the DB query takes 5 seconds
When: the deadline expires mid-query
Then: the server handler detects ctx.Err() == DeadlineExceeded
      AND cancels the DB query (passes context to DB driver)
      AND the connection is returned to the pool (no leak)

Given: a proto field is removed from a published message
When: the proto is updated
Then: the field number is added to a 'reserved' declaration
      AND a new field number is assigned for any replacement field
      AND the package version is bumped to v2 if the removal is a breaking change
```
