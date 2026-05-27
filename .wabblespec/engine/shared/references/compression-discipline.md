# Compression Discipline

Three compression levels for module output. Applied when output exceeds the inline threshold. Consumers: Economy, Homowabian, all output-producing modules.

## Levels

### lite
Remove filler words, transition sentences, and redundant restatements. Preserve all facts. Readable prose. Suitable for 500–2000 token outputs.

Drop: "This means that...", "In other words...", "As mentioned above...", "It is worth noting that..."
Keep: all technical terms, identifiers, values, constraints.

### full
Compress to information-minimal form. Short sentences. No articles where avoidable. Fragments acceptable for lists. Dense. Suitable for 200–500 token summaries of larger content.

Pattern: `[thing] [action] [reason]. [next step].`
Not: "The authentication module encountered an issue with token validation."
Yes: "Auth module failed token validation. Check expiry logic."

### ultra
Maximum compression. Bullet list or table only. No prose except where prose carries unique information not expressible as a list item. Suitable for index entries, receipt summaries, and status lines.

## Mechanical hedge detection

Strip these regardless of compression level:

| Hedge phrase | Replace with |
|---|---|
| "It seems like..." | State it directly |
| "You might want to..." | Imperative: "Do X." |
| "Generally speaking..." | Drop entirely |
| "In most cases..." | Drop if the exception is not being described |
| "Feel free to..." | Drop entirely |
| "Of course..." | Drop entirely |
| "Please note that..." | Drop entirely |
| "It's important to..." | Drop — importance is shown by placement, not stated |

## Grammar rules under compression

- Drop articles (a, an, the) where meaning is preserved
- Prefer active voice: "Guard blocks the operation" not "the operation is blocked by Guard"
- Replace passive constructions: "It is required that X" → "X is required"
- Shorten: "in order to" → "to", "at this point in time" → "now", "due to the fact that" → "because"

## What is never compressed

- Error text (always verbatim)
- Code blocks (always verbatim)
- Schema field names
- Enum values
- File paths and identifiers
- User-declared requirements (quoted requirements are locked)
