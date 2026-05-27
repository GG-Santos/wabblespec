# Version Tracking

Semver automation protocol. Archive has exclusive write authority over `.wabblespec/VERSION`. No other module may increment the version.

## VERSION file

Single line: `MAJOR.MINOR.PATCH` (e.g. `0.3.1`). No prefix, no suffix, no trailing newline required.

## Semver bump rules

| Signal | Bump |
|---|---|
| Any receipt in the session has `change_class: BREAKING` | Major (`x.0.0`) |
| Any receipt has `change_class: ADDITIVE` or `DEPRECATION`, no BREAKING | Minor (`0.x.0`) |
| Only `change_class: COSMETIC` or no change classification | Patch (`0.0.x`) |

Worst signal wins. One BREAKING signal in a session with 10 COSMETIC signals → major bump.

## Version read authority

Any module may read `.wabblespec/VERSION`. Only Archive writes it.

## Version in receipts

Archive records `version_previous` and `version_new` in the delivery receipt. Downstream consumers (CHANGELOG.md, Release module, API contract) read the delivery receipt for version context — they do not read VERSION directly.

## Pre-release versions

Pre-release suffix: `MAJOR.MINOR.PATCH-<label>` (e.g. `0.4.0-beta.1`). Archive appends the suffix when the delivery receipt has `pre_release: true`. Pre-release versions do not count as the stable version — the next Archive run that omits `pre_release` promotes the pre-release to stable.

## Version 0.x.x convention

While MAJOR is 0, the framework is in development. BREAKING changes increment MINOR (not MAJOR) in 0.x.x versioning. Once MAJOR reaches 1 (promoted by a deliberate Forge promotion with human sign-off), standard semver applies.

## CHANGELOG entry association

Each CHANGELOG entry references the version it was cut at. Archive writes the entry at the same time as the version bump. They are atomic — a CHANGELOG entry without a version bump, or a version bump without a CHANGELOG entry, is a violation of this protocol.
