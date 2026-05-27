# Java Reference

> **Type:** Language reference | Loaded by platform packages on demand.

---

## Toolchain

| Tool | Decision | Notes |
|---|---|---|
| Version | Java 21 LTS | Use virtual threads (Project Loom) for I/O concurrency |
| Build | Gradle with Kotlin DSL (`build.gradle.kts`) | Not Groovy DSL — Kotlin DSL has type safety |
| Lint | Checkstyle + SpotBugs | Config committed |
| Format | google-java-format / Spotless | `./gradlew spotlessCheck` in CI |
| Test | JUnit 5 + AssertJ | |
| Dependency versions | Version catalog (`libs.versions.toml`) | Single source for all dep versions |

---

## Gradle Kotlin DSL (minimal)

```kotlin
// build.gradle.kts
plugins {
    java
    application
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

dependencies {
    implementation(libs.guava)
    testImplementation(libs.junit.jupiter)
}

tasks.test {
    useJUnitPlatform()
}
```

```toml
# gradle/libs.versions.toml
[versions]
junit = "5.10.2"

[libraries]
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }
```

---

## Records for Immutable Data

Java 21: use Records instead of hand-written POJOs for immutable value types.

```java
// Record — immutable, auto-generates constructor, accessors, equals, hashCode, toString
public record User(String id, String email, Instant createdAt) {
    // Compact constructor for validation
    public User {
        Objects.requireNonNull(id, "id must not be null");
        if (email.isBlank()) throw new IllegalArgumentException("email blank");
    }
}

// Sealed interfaces for algebraic types
public sealed interface Result<T> permits Result.Ok, Result.Err {
    record Ok<T>(T value) implements Result<T> {}
    record Err<T>(String reason) implements Result<T> {}
}
```

---

## Virtual Threads (Java 21)

For I/O-bound services: virtual threads replace thread pools.

```java
// Old: fixed thread pool (limits concurrency)
ExecutorService pool = Executors.newFixedThreadPool(200);

// New: virtual thread executor (scales to millions)
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

// Spring Boot 3.2+: enable in application.properties
// spring.threads.virtual.enabled=true
```

**Pinning:** Virtual threads pin to carrier thread when synchronized block holds a monitor. Use `ReentrantLock` instead of `synchronized` in virtual-thread-heavy code.

---

## Null Safety

Java has no built-in null safety. Use annotations to communicate intent:

```java
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;

public @Nullable String findUser(@NonNull String id) { ... }
```

Or use `Optional<T>` for return types that may be absent:
```java
public Optional<User> findById(String id) {
    return Optional.ofNullable(repository.get(id));
}
// Caller: findById(id).ifPresent(user -> ...);
// Never: findById(id).get()  — throws NoSuchElementException
```

---

## Non-Negotiable Rules

1. Gradle Kotlin DSL — not Groovy. Type safety catches config errors at IDE time.
2. `libs.versions.toml` version catalog — single place for all dependency versions.
3. Java 21 toolchain pinned in `build.gradle.kts` — not system Java.
4. Records for immutable data — eliminate hand-written equals/hashCode.
5. No raw types: `List` → `List<String>`. Generics always specified.
6. `Optional.get()` without `isPresent()` check is a bug — use `orElseThrow()` with message.

---

## Common Failure Modes

| Failure | Cause | Fix |
|---|---|---|
| Build not reproducible | System Java version varies | Pin via `java.toolchain.languageVersion` |
| NullPointerException at runtime | Missing null check | `Optional<T>`, JSpecify annotations, or explicit check |
| Virtual thread pinning | `synchronized` block + blocking I/O | Replace `synchronized` with `ReentrantLock` |
| Dependency version conflicts | Multiple versions of same library | Use `./gradlew dependencies` to audit; enforce via BOM |
| Test ordering dependency | Tests share static state | Use `@BeforeEach` to reset; avoid static mutable fields |
