# Framework-Specific Architecture: Swift (SwiftUI + UIKit)

> **Applies when:** `.xcodeproj` or `.xcworkspace` detected + Swift files + no Flutter/RN detected.
> Covers iOS/iPadOS native development. Declare SwiftUI vs UIKit vs hybrid in technical-spec.md.
> **Version authority:** Swift 5.9+. SwiftUI for iOS 17+ target. UIKit for iOS 15+ compatibility. Swift Concurrency (async/await) is the default — DispatchQueue and closures are legacy patterns.

---

## UI Framework Declaration [REQUIRED]

SwiftUI and UIKit have different architecture patterns. Declare the primary framework before implementation.

| Choice | When to use |
|---|---|
| **SwiftUI** | iOS 16+ minimum deployment target; new screens in new projects |
| **UIKit** | iOS 14-15 support required; complex custom animations; existing UIKit codebase |
| **Hybrid** | SwiftUI for new screens embedded via `UIHostingController`; UIKit for existing screens |

**Declared framework:** ___

**Minimum deployment target:** ___

---

## SwiftUI Architecture

```swift
// MVVM — ViewModel is an ObservableObject
@MainActor
final class ProductListViewModel: ObservableObject {
    @Published private(set) var products: [Product] = []
    @Published private(set) var isLoading = false
    @Published private(set) var error: String?

    private let repository: ProductRepository

    init(repository: ProductRepository = ProductRepository()) {
        self.repository = repository
    }

    func loadProducts() async {
        isLoading = true
        error = nil
        do {
            products = try await repository.fetchAll()
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }
}

// View — thin; no business logic
struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                ErrorView(message: error)
            } else {
                List(viewModel.products) { product in
                    ProductRow(product: product)
                }
            }
        }
        .task { await viewModel.loadProducts() }  // preferred over .onAppear for async
    }
}
```

**`@StateObject` vs `@ObservedObject`:**
- `@StateObject` — the view owns the lifetime. Use when the view creates the ViewModel.
- `@ObservedObject` — the object is passed in from outside. Use when the parent creates the ViewModel.
- Never use `@ObservedObject` for a ViewModel the view creates — it will be destroyed and recreated unexpectedly.

---

## Property Wrappers

```swift
@State          // local view state — simple value types (Bool, String, Int)
@Binding        // two-way binding from parent to child — passed as $value
@StateObject    // reference type owned by this view (ViewModel)
@ObservedObject // reference type owned by parent, passed in
@EnvironmentObject // injected from ancestor — avoids prop drilling; use sparingly
@Environment(\.colorScheme) var colorScheme  // system environment values
@AppStorage("hasOnboarded") var hasOnboarded = false  // UserDefaults binding
```

**Rule:** `@EnvironmentObject` breaks compile-time safety (crash if not injected). Prefer dependency injection via initializer for ViewModels. Reserve `@EnvironmentObject` for truly app-wide concerns (auth state, theme).

---

## Swift Concurrency

```swift
// async/await — preferred over closures and DispatchQueue
func fetchProduct(id: String) async throws -> Product {
    let url = URL(string: "https://api.example.com/products/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw APIError.badStatus
    }
    return try JSONDecoder().decode(Product.self, from: data)
}

// Task — for fire-and-forget in non-async context
// .task modifier on View is preferred — auto-cancelled on disappear
.task {
    await viewModel.loadProducts()
}

// @MainActor — ensures UI updates happen on main thread
@MainActor
func updateUI() {
    self.products = newProducts  // safe — on main thread
}

// Actor — for shared mutable state across concurrent code
actor Cache {
    private var storage: [String: Data] = [:]
    func set(_ key: String, value: Data) { storage[key] = value }
    func get(_ key: String) -> Data? { storage[key] }
}
```

**Never use `DispatchQueue.main.async` in new code.** Use `@MainActor` annotations or `await MainActor.run { }` instead. `DispatchQueue` predates Swift Concurrency and does not compose with `async/await`.

---

## Data Persistence

```swift
// SwiftData (iOS 17+) — preferred for new projects
import SwiftData

@Model
final class Product {
    var id: String
    var name: String
    var price: Double
    init(id: String, name: String, price: Double) { ... }
}

// ModelContainer setup in App
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: Product.self)
    }
}

// Usage in View
@Query private var products: [Product]
@Environment(\.modelContext) private var context

// Core Data (iOS 15-16 compatibility)
// Use NSPersistentCloudKitContainer for CloudKit sync
// Wrap in a repository — never call NSManagedObjectContext directly from views
```

**Rule:** Views never call persistence APIs directly. All persistence operations go through a repository or ViewModel. This keeps views testable without a real database.

---

## Navigation (SwiftUI)

```swift
// NavigationStack (iOS 16+) — type-safe path-based navigation
struct AppView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Product.self) { product in
                    ProductDetailView(product: product)
                }
                .navigationDestination(for: Route.self) { route in
                    // enum-based routing
                }
        }
    }
}
```

**Deep linking:** Declare URL schemes and Universal Links in `Info.plist`. Handle in `onOpenURL`. Map URL to a `NavigationPath` state update — do not navigate imperatively.

---

## GWT Acceptance Scenarios

```
Given: a ViewModel publishes state changes
When: an async operation completes on a background thread
Then: @Published properties are updated on the main thread (@MainActor)
      AND the view updates without "Publishing changes from background threads" warnings
      AND no DispatchQueue.main.async is used — @MainActor is used instead

Given: data is fetched in a SwiftUI View
When: the view disappears before the fetch completes
Then: the .task modifier cancels the in-flight Task automatically
      AND no completion handler fires after the view is deallocated
      AND no retain cycles exist from captured [weak self] patterns (not needed with structured concurrency)

Given: the app persists user data
When: the persistence layer is accessed
Then: the call goes through a repository (not directly from a View or ViewModel to NSManagedObjectContext)
      AND the repository is injectable (protocol-based) for testing
      AND tests can substitute a mock repository without a real database
```
