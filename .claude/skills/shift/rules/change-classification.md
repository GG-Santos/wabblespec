# Change Classification

Every spec change gets exactly one class. Classification is conservative — when in doubt, upgrade to the higher class.

## BREAKING

A change that requires existing consumers to update their implementation.

**Examples:**
- Removing a required field from an output schema
- Renaming an existing interface, module ID, or receipt field
- Changing the type of an existing field (string → integer)
- Removing a supported mode or enum value
- Making a previously optional field required
- Inverting the meaning of a boolean flag

**Effect:** Triggers loop-back. Downstream consumers must be identified and notified. `loop_back_required: true` in receipt.

---

## DEPRECATION

A change that marks existing functionality for removal but does not remove it yet. Consumers can continue using it but must plan migration.

**Examples:**
- Adding a deprecation notice to an existing field with a sunset date
- Marking a module mode as deprecated (still functional, replacement documented)
- Adding `deprecated: true` to schema fields alongside replacement field

**Effect:** Records `deprecations_added` in receipt. Does not trigger loop-back unless deprecation period is immediate (sunset = this version).

---

## ADDITIVE

A change that adds new fields, modes, or capabilities without removing or modifying existing ones.

**Examples:**
- Adding a new optional field to a schema
- Adding a new mode to a module that has no existing mode of that name
- Adding a new rule file, agent, or script to a module
- Adding a new `depends_on` entry in framework.yaml

**Effect:** Consumers must be checked if the addition is to a shared schema consumed by multiple modules. `downstream_consumers_affected` count may be > 0.

---

## COSMETIC

A change that affects presentation, documentation, or wording only — no behavioral or structural change.

**Examples:**
- Rewording a comment or description field
- Reformatting a SKILL.md section
- Fixing a typo in a rule file
- Reordering fields in documentation (not in schema — schema order matters)

**Effect:** No loop-back. No downstream impact. Patch version bump only.

---

## Classification decision tree

1. Does any existing consumer break without code change? → BREAKING
2. Is existing functionality deprecated with a sunset date? → DEPRECATION
3. Is new functionality added without touching existing? → ADDITIVE
4. Is only presentation/wording changed? → COSMETIC
