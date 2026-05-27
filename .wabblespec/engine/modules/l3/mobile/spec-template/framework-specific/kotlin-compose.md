# Framework-Specific Architecture: Kotlin (Jetpack Compose)

> **Applies when:** `.gradle` files detected + `kotlin` language + `compose` dependency in build.gradle.
> Covers Android native with Jetpack Compose + modern Android architecture (MVVM, Hilt, Coroutines).
> **Version authority:** Compose BOM 2024.x. Kotlin 1.9+. Target SDK 34+. min SDK declare below.

---

## Architecture Declaration [REQUIRED]

Declare minimum SDK and architecture choices before implementation.

**Minimum SDK version:** ___  (affects available APIs; 24+ for 98% coverage as of 2024)
**Target SDK:** ___ (must be current year's release or prior)

**Architecture:** MVVM with:
- `ViewModel` (Jetpack) — survives configuration changes; owns UI state
- `StateFlow` / `SharedFlow` — reactive streams from ViewModel to Compose
- `Repository` — data access abstraction (separates data sources from ViewModels)
- `Hilt` — dependency injection (declare if used; alternative: manual DI or Koin)

---

## Jetpack Compose Fundamentals

```kotlin
// Composable function — no class, no lifecycle; declarative UI
@Composable
fun ProductCard(
    product: Product,
    onAddToCart: (Product) -> Unit,  // lambda props — not ViewModel references
    modifier: Modifier = Modifier    // always accept Modifier as last param; default = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = product.name, style = MaterialTheme.typography.titleMedium)
            Text(text = "$${product.price}", style = MaterialTheme.typography.bodyLarge)
            Button(onClick = { onAddToCart(product) }) {
                Text("Add to cart")
            }
        }
    }
}

// State hoisting — state lives in caller; composable is stateless
@Composable
fun SearchBar(
    query: String,           // state comes in
    onQueryChange: (String) -> Unit,  // events go out
    modifier: Modifier = Modifier
) {
    TextField(value = query, onValueChange = onQueryChange, modifier = modifier)
}
```

**State hoisting rule:** Composables are stateless when possible. State is hoisted to the lowest ancestor that needs it, ultimately to the ViewModel. Never call `ViewModel` functions from low-level composables — pass lambdas instead.

---

## ViewModel and StateFlow

```kotlin
@HiltViewModel  // if using Hilt
class ProductListViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {

    // Sealed class for UI state
    sealed class UiState {
        object Loading : UiState()
        data class Success(val products: List<Product>) : UiState()
        data class Error(val message: String) : UiState()
    }

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    private fun loadProducts() {
        viewModelScope.launch {
            try {
                val products = productRepository.fetchAll()
                _uiState.value = UiState.Success(products)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// In Composable — collect as State
@Composable
fun ProductListScreen(viewModel: ProductListViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is ProductListViewModel.UiState.Loading -> CircularProgressIndicator()
        is ProductListViewModel.UiState.Success -> ProductList(state.products)
        is ProductListViewModel.UiState.Error -> ErrorMessage(state.message)
    }
}
```

**`collectAsStateWithLifecycle` vs `collectAsState`:** Use `collectAsStateWithLifecycle` — it stops collection when the app is backgrounded, saving battery and preventing background processing. Requires `lifecycle-runtime-compose` dependency.

---

## Navigation Compose

```kotlin
// navigation/AppNavGraph.kt
@Composable
fun AppNavGraph(navController: NavHostController) {
    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onProductClick = { id -> navController.navigate("products/$id") })
        }
        composable(
            route = "products/{productId}",
            arguments = listOf(navArgument("productId") { type = NavType.StringType })
        ) { backStackEntry ->
            val productId = backStackEntry.arguments?.getString("productId")!!
            ProductDetailScreen(productId = productId)
        }
    }
}

// Type-safe navigation (Compose Navigation 2.8+)
@Serializable object Home
@Serializable data class ProductDetail(val productId: String)
```

**Deep links:** Declare intent filters in `AndroidManifest.xml`. Add `deepLinks` to composable route declarations. Test deep links with `adb shell am start -d "myapp://products/123"`.

---

## Coroutines and Flow

```kotlin
// Repository with Flow — reactive data stream
class ProductRepository(private val dao: ProductDao, private val api: ApiService) {

    // Flow from Room — emits on every DB change
    fun observeProducts(): Flow<List<Product>> = dao.observeAll()

    // One-shot suspend function
    suspend fun fetchAndSave() {
        val products = api.getProducts()
        dao.insertAll(products)
    }
}

// ViewModel consuming Flow
val products: StateFlow<List<Product>> = productRepository
    .observeProducts()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),  // stop 5s after last subscriber
        initialValue = emptyList()
    )
```

**Dispatcher rules:**
- `Dispatchers.Main` — UI updates, ViewModel operations (default in `viewModelScope`)
- `Dispatchers.IO` — network calls, disk I/O (use `withContext(Dispatchers.IO)` in repository)
- `Dispatchers.Default` — CPU-intensive work (sorting large lists, parsing)
- Never block `Main` dispatcher — no `Thread.sleep`, no blocking I/O on Main

---

## Hilt Dependency Injection

```kotlin
@HiltAndroidApp
class MyApplication : Application()  // required in AndroidManifest.xml

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(ApiService::class.java)
}

// Inject into ViewModel
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel()

// Inject into Activity/Fragment
@AndroidEntryPoint
class MainActivity : ComponentActivity()
```

---

## GWT Acceptance Scenarios

```
Given: the ViewModel exposes UiState as StateFlow
When: a network call completes
Then: the StateFlow emits the new state on the main dispatcher
      AND the Composable collecting via collectAsStateWithLifecycle recomposes
      AND no UI update happens when the app is in the background

Given: a composable receives state and events via parameters
When: the composable is tested in isolation
Then: the test can provide arbitrary state without a real ViewModel
      AND events are captured via lambda stubs
      AND no Hilt injection is required for composable unit tests

Given: the repository makes a network call
When: the call is in progress
Then: the work runs on Dispatchers.IO (not Main)
      AND the ViewModel's StateFlow shows Loading state during the call
      AND cancellation of the coroutine scope stops the in-flight call
```
