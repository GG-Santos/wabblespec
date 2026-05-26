# Kotlin / Jetpack Compose (Native Android)

Loaded by Apply when build.gradle or AndroidManifest.xml is detected.

## Version baseline

Kotlin 1.9+; Jetpack Compose for new UI; Views (XML) for legacy codebases.

## Architecture — MVVM + Clean

Standard Android architecture (Google recommended):

```
UI layer        — Composables + ViewModel
Domain layer    — Use cases (optional for simple apps)
Data layer      — Repositories + Data sources (Room, Retrofit)
```

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    
    val uiState: StateFlow<ProfileUiState> = userRepository
        .getUserStream()
        .map { ProfileUiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ProfileUiState.Loading)
    
    fun refresh() {
        viewModelScope.launch {
            userRepository.refresh()
        }
    }
}
```

## Jetpack Compose patterns

```kotlin
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    when (uiState) {
        is ProfileUiState.Loading -> CircularProgressIndicator()
        is ProfileUiState.Success -> UserContent(uiState.user)
        is ProfileUiState.Error -> ErrorScreen(uiState.message)
    }
}
```

- `collectAsStateWithLifecycle()` — stops collecting when UI is in background (battery-efficient)
- Hoisted state: pass state down, events up — composables are pure functions of their parameters
- `remember` — survives recomposition; `rememberSaveable` — survives process death

## Navigation — Compose Navigation

```kotlin
NavHost(navController, startDestination = "home") {
    composable("home") { HomeScreen(navController) }
    composable("profile/{id}") { backStack ->
        val id = backStack.arguments?.getString("id")
        ProfileScreen(id, navController)
    }
}
```

Declare all routes in spec including argument types and deep link patterns.

## Dependency injection — Hilt

Hilt (Dagger wrapper) is the standard DI solution for Android. Declare:
- Which modules provide which dependencies
- Which components scope them (Singleton, ActivityScoped, ViewModelScoped)

## Coroutines and Flow

```kotlin
// Repository
fun getUserStream(): Flow<User> = userDao.observeUser()

// One-shot async
suspend fun fetchUser(id: String): User = withContext(Dispatchers.IO) {
    api.getUser(id)
}

// ViewModel scope
viewModelScope.launch {
    val user = repository.fetchUser(id)
    // runs in Main dispatcher by default
}
```

- `Dispatchers.IO` — blocking I/O (network, disk)
- `Dispatchers.Default` — CPU-intensive work
- `Dispatchers.Main` — UI updates

## Data persistence

| Use | Tool |
|---|---|
| User preferences | DataStore (replaces SharedPreferences) |
| Credentials / tokens | EncryptedSharedPreferences or Keystore |
| Structured local data | Room (SQLite ORM) |
| Files | Internal storage (getFilesDir) or external (MediaStore API) |

## Testing

```kotlin
@Test
fun profileViewModel_loading_showsCorrectState() = runTest {
    val viewModel = ProfileViewModel(FakeUserRepository())
    assertEquals(ProfileUiState.Loading, viewModel.uiState.value)
}
```

- JUnit4 + `kotlinx.coroutines.test` for ViewModel tests
- Compose UI testing: `createComposeRule()` + `onNodeWithText()`, `performClick()`
- Espresso for instrumentation tests on device (use sparingly — slow)
