# Platform: Library / Package

Reusable library or package target (npm, pip, gem, crate, etc.). Activates when Recipe identifies a library, SDK, or package as the primary build target.

**Skill:** `modules/l3/library/SKILL.md`

## What makes Library different

| Concern | Library approach |
|---------|----------------|
| API stability | Public API surface versioned strictly — no accidental breaking changes |
| Semver discipline | Every release classified: patch/minor/major per semver spec |
| Documentation | Public API fully documented — no undocumented public surface |
| Dependency hygiene | Minimal dependencies; peer dependencies declared correctly |
| Tree-shaking | Exports structured for tree-shaking if JS package |
| Backwards compat | Deprecation path declared before removal — minimum one minor version warning |
| Bundle impact | Size impact declared for JS packages |

## Platform-specific spec sections

- Public API contract: every exported symbol documented with types and behavior
- Semver classification: change type for every proposed modification (PATCH/MINOR/MAJOR)
- Deprecation notices: symbols being deprecated with migration path and timeline
- Peer dependency contract: what versions of peer deps are compatible and tested
- Entry points: main, module, exports map — declared for JS packages
- Test coverage requirements: public API must have test coverage; private internals may vary

## Security controls loaded

- Dependency supply chain: new dependencies reviewed for known CVEs and maintenance status
- Prototype pollution: object spread and merge operations validated (JS packages)
- Serialization: any `eval()`, `new Function()`, or dynamic code execution flagged as BLOCK
- Publishing: package registry credentials in CI secrets — never in package.json or setup.py

## Gateway interaction

Library targets typically activate:
- `gateway-security` — supply chain and serialization surface
- `gateway-engineering` — always (API contract, semver discipline)

Library targets do not activate aesthetic, design, or experience gateways.
