# Go Reference

> **Type:** Language reference | Loaded by platform packages on demand.

---

## Toolchain

| Tool | Decision | Notes |
|---|---|---|
| Version | 1.22+ | Go toolchain pinned in `go.mod` via `toolchain` directive |
| Format | `gofmt` / `goimports` | Non-negotiable — enforced in CI |
| Lint | `golangci-lint` | Config committed as `.golangci.yml` |
| Test | `go test ./...` | Table-driven tests standard |
| Build | `go build` | CGO disabled by default unless required |

---

## Module Setup

```
go.mod — committed
go.sum — committed (both files always committed together)

Never: go mod vendor unless explicitly required by deployment target
```

`go.mod` sets minimum Go version:
```
module github.com/org/repo

go 1.22

toolchain go1.22.3
```

---

## Error Handling

Go errors are values. Handle them explicitly — never ignore.

```go
// Good: handle or propagate with context
result, err := doThing(ctx)
if err != nil {
    return fmt.Errorf("doThing: %w", err)  // wrap with %w for unwrap support
}

// Bad: ignoring error
result, _ := doThing(ctx)  // forbidden unless documented reason
```

**`fmt.Errorf("context: %w", err)` wraps for `errors.Is` / `errors.As` unwrapping.** Always wrap with context at call sites.

---

## Goroutine Lifecycle

Every goroutine must have a defined lifecycle — creation, work, and termination.

```go
// Use context for cancellation
func runWorker(ctx context.Context, jobs <-chan Job) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case job, ok := <-jobs:
            if !ok {
                return nil  // channel closed
            }
            if err := process(job); err != nil {
                return fmt.Errorf("process job %v: %w", job.ID, err)
            }
        }
    }
}

// Track goroutines with WaitGroup
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    runWorker(ctx, jobs)
}()
wg.Wait()
```

**Never launch a goroutine without knowing how it terminates.** Goroutine leak = memory leak.

---

## Table-Driven Tests

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

---

## Non-Negotiable Rules

1. `go.mod` and `go.sum` both committed — reproducible builds.
2. No ignored errors (`_, _` or `_ =`) without comment explaining why.
3. Context passed as first argument to all functions doing I/O or network calls.
4. `gofmt`/`goimports` enforced in CI — no style debates.
5. No `init()` functions with side effects — use explicit initialization.
6. Exported identifiers have godoc comments (`// FuncName does X`).

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Race condition | Shared map or slice without mutex | Use `sync.RWMutex` or channel; `go test -race` |
| Goroutine leak | No cancellation path | Always pass `context.Context`, select on `ctx.Done()` |
| Non-deterministic test | Global state mutated between tests | Reset state in `t.Cleanup` or use subtests |
| Nil pointer panic | Interface nil check wrong | Check underlying type: `v == nil` vs `interface{}(nil)` |
| Import cycle | Circular package dependencies | Extract shared types to third package |
