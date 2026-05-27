# Brand Standards

## Brand Asset Source of Truth

Brand assets declared in spec at P1:
- Logo: source file format and location
- Wordmark: approved variants (horizontal, stacked, icon-only)
- Color palette: primary brand colors with hex/RGB/HSL values
- Source of truth: design tool (Figma, Sketch) or committed asset directory

No brand assets embedded in code as inline values. All brand colors become design tokens.

## Brand Voice Consistency

Brand voice declared in P1 Design Document and referenced by Expression layer. Aesthetic enforces visual brand consistency; Expression layer (Homowabian) enforces voice consistency. Coordinated — neither overrides the other.

## Asset Usage Rules

- Approved formats declared (SVG for web, PDF/EPS for print, PNG with declared minimum size)
- Minimum size declared per logo variant (below minimum = use alternate variant)
- Clear space: declared multiplier of the logo's X-height or declared unit
- Prohibited treatments listed explicitly (no stretching, no recoloring, no drop shadows)

## Audit Gates

- [ ] Brand asset source of truth declared in P1 spec
- [ ] Logo source file format and location declared
- [ ] All brand colors declared as design tokens (not inline values)
- [ ] Minimum size declared per logo variant
- [ ] Clear space rules declared
- [ ] Prohibited treatments listed
