# Flutter Framework

Loaded by Apply when pubspec.yaml with flutter dependency is detected.

## Version baseline

Flutter 3.19+ / Dart 3.x. Sound null safety required.

## Architecture decisions spec must declare

- **State management**: Bloc/Cubit (recommended for complex apps), Provider, Riverpod, or GetX
- **Navigation**: GoRouter (recommended, supports deep links) or Navigator 2.0 directly
- **Dependency injection**: GetIt, Injectable, or Riverpod providers
- **Platform channels**: which, if any, native integrations are required

## Widget model

Everything is a widget. Key distinctions:
- `StatelessWidget`: pure function of its inputs; rebuild is cheap
- `StatefulWidget`: has mutable `State`; `setState()` triggers rebuild of the widget subtree
- `InheritedWidget`: base for propagating data down the tree (Context providers wrap this)

Performance: minimize subtree rebuild scope. `const` constructors prevent unnecessary rebuilds.

## State management — Bloc/Cubit

```dart
// Cubit (simpler, no events)
class CounterCubit extends Cubit<int> {
  CounterCubit() : super(0);
  void increment() => emit(state + 1);
}

// Bloc (events + states)
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(CounterInitial()) {
    on<IncrementPressed>((event, emit) => emit(CounterUpdated(state.count + 1)));
  }
}
```

Spec must declare: which Blocs/Cubits manage which domain; whether state is shared globally or scoped to a subtree.

## Navigation — GoRouter

```dart
final router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomePage()),
    GoRoute(
      path: '/profile/:id',
      builder: (_, state) => ProfilePage(id: state.pathParameters['id']!),
    ),
  ],
  redirect: (_, state) {
    final isLoggedIn = authState.isAuthenticated;
    if (!isLoggedIn && !state.matchedLocation.startsWith('/login')) return '/login';
    return null;
  },
);
```

Declare all routes in spec including redirect logic for auth.

## Platform channels

When calling native code:

```dart
// Dart side
const channel = MethodChannel('com.example/feature');
final result = await channel.invokeMethod<String>('doNativeThing', {'param': value});

// iOS: AppDelegate or FlutterViewController registration
// Android: MainActivity or FlutterActivity registration
```

Declare channel name, method names, and argument/return types in spec.

## Performance

- `const` widgets: use everywhere possible — compile-time constant widgets skip rebuild
- ListView.builder: for long lists — do not `children: items.map((i) => Widget(i)).toList()`
- Image.network: use CachedNetworkImage for caching
- Heavy computation: use `compute()` to run in a separate isolate (Dart has no shared memory — isolates communicate by message passing)

## Testing

```dart
testWidgets('counter increments', (tester) async {
  await tester.pumpWidget(const MyApp());
  expect(find.text('0'), findsOneWidget);
  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();
  expect(find.text('1'), findsOneWidget);
});
```

- Widget tests: `testWidgets` with `WidgetTester`
- Unit tests: `test()` for Blocs, Cubits, use cases
- Integration tests: `integration_test` package on device
