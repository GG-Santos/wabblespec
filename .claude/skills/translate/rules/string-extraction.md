# String Extraction

What qualifies as a translatable string. Applied in Translate extract mode.

## Qualifies for extraction

- Text displayed to users in the UI
- Error messages
- Notification text
- Email subject lines and body templates
- Tooltip content
- Empty state text
- Confirmation dialog text
- Accessibility labels (aria-label, aria-description, alt text)
- Placeholder text in form fields
- Section headings visible to users

## Does not qualify for extraction

- Code identifiers (variable names, function names, class names)
- Enum values used as code constants (even if they look like words)
- CSS class names and IDs
- Database column names
- Log messages (internal, not user-visible)
- API response keys
- Configuration keys
- File paths and URLs
- Numeric values without surrounding text
- Strings already wrapped in a no-translate directive (`<span translate="no">`)

## Extraction heuristics

When scanning source files, use these signals to identify user-visible strings:

- Strings passed to i18n functions: `t()`, `intl.formatMessage()`, `NSLocalizedString()`, `getString()`
- Strings assigned to UI properties: `label=`, `placeholder=`, `title=`, `alt=`, `aria-label=`
- Strings in JSX text nodes (direct children of UI components)

Do not extract strings inside:
- `console.log()`, `logger.*()`, `print()` calls
- Comments
- Test assertions
- Type definitions and interfaces

## Key naming convention

Keys follow dot-separated namespace format: `{component}.{context}.{variant}`

- `auth.login.submit_button` — login form submit button
- `auth.login.error.invalid_credentials` — login error for invalid credentials
- `dashboard.empty_state.title` — dashboard empty state title
- `settings.account.delete_confirmation` — account deletion confirmation text

All segments are lowercase, underscore-separated. No camelCase in keys.
