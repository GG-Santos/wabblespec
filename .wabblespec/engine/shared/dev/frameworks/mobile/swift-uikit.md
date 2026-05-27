# Swift / SwiftUI / UIKit (Native iOS)

Loaded by Apply when .xcodeproj or Package.swift is detected.

## Version baseline

Swift 5.9+; SwiftUI for new UI code; UIKit for existing codebases and capabilities not yet in SwiftUI.

## UI framework choice

| Feature | SwiftUI | UIKit |
|---|---|---|
| Layout | Declarative, `@State` driven | Imperative, delegate-based |
| Animation | Built-in, declarative | Manual CAAnimation / UIViewPropertyAnimator |
| Composition | Views composed from smaller views | ViewControllers + child VCs |
| Data binding | `@Binding`, `@ObservableObject`, `@Observable` | Manual KVO / delegate / NotificationCenter |
| Interop | UIViewRepresentable to wrap UIKit views | UIHostingController to embed SwiftUI |

Spec must declare: SwiftUI vs UIKit per major screen/module.

## Architecture (SwiftUI)

Recommended: MVVM with `@Observable` (Swift 5.9+):

```swift
@Observable
class ProfileViewModel {
    var user: User?
    var isLoading = false
    
    func load(id: String) async {
        isLoading = true
        defer { isLoading = false }
        user = try? await userService.fetch(id: id)
    }
}

struct ProfileView: View {
    @State private var viewModel = ProfileViewModel()
    
    var body: some View {
        if viewModel.isLoading {
            ProgressView()
        } else if let user = viewModel.user {
            Text(user.name)
        }
    }
}
```

## Concurrency — Swift async/await

```swift
// async function
func fetchUser(id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Task for launching async work from sync context
Task {
    do {
        let user = try await fetchUser(id: "123")
    } catch {
        // handle error
    }
}

// MainActor for UI updates
@MainActor
class ViewModel: ObservableObject {
    @Published var user: User?
}
```

All UI updates must happen on the main actor. `@MainActor` annotation enforces this at compile time.

## Data persistence

| Use | Tool |
|---|---|
| User preferences | UserDefaults (small values, non-sensitive) |
| Credentials / tokens | Keychain (always — never UserDefaults for sensitive data) |
| Structured data | Core Data or SwiftData (Swift 5.9+) |
| Files | FileManager in Documents (user data) or Caches (reconstructable) |

## Navigation — SwiftUI

```swift
NavigationStack {
    List(items) { item in
        NavigationLink(item.title, value: item)
    }
    .navigationDestination(for: Item.self) { item in
        ItemDetailView(item: item)
    }
}
```

`NavigationStack` + `.navigationDestination` for Swift 5.6+. Declare the navigation graph in spec.

## Testing

- `XCTestCase` for unit tests (ViewModels, services, utilities)
- `XCUITest` for UI automation (critical user flows; expensive — be selective)
- Mock dependencies via protocols — inject fakes in tests
